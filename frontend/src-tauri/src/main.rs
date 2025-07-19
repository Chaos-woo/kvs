
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use std::process::{Command, Child};
use tauri::{WindowEvent};

fn main() {
  // 创建共享的后端进程句柄
  let backend_child: Arc<Mutex<Option<Child>>> = Arc::new(Mutex::new(None));
  let backend_child_clone = backend_child.clone();

  tauri::Builder::default()
    .setup(move |_app| {
      // 仅在生产环境中启动内置后端
      #[cfg(not(debug_assertions))]
      {
        let backend_child_setup = backend_child.clone();
        // 使用 Tauri 的 sidecar 功能启动后端
        thread::spawn(move || {
          println!("Starting backend process...");

          match Command::new("kvs_backend.exe").spawn() {
            Ok(child) => {
              println!("Backend process started successfully");

              // 存储后端进程句柄
              {
                let mut backend_guard = backend_child_setup.lock().unwrap();
                *backend_guard = Some(child);
              }
            },
            Err(e) => {
              eprintln!("Failed to spawn backend process: {}", e);
            }
          }
        });
      }

      Ok(())
    })
    .on_window_event(move |event| {
      match event.event() {
        WindowEvent::CloseRequested { .. } => {
          println!("Window close requested, terminating backend...");

          // 终止后端进程
          #[cfg(not(debug_assertions))]
          {
            // 首先尝试优雅关闭
            println!("Attempting graceful shutdown via HTTP endpoint...");
            let graceful_shutdown = std::thread::spawn(|| {
              // 使用PowerShell的Invoke-RestMethod尝试优雅关闭
              match std::process::Command::new("powershell")
                .args(&["-Command", "try { Invoke-RestMethod -Uri 'http://127.0.0.1:5000/shutdown' -Method POST -TimeoutSec 3 } catch { Write-Host 'Shutdown request failed' }"])
                .output() {
                Ok(output) => {
                  if output.status.success() {
                    println!("Graceful shutdown request sent successfully");
                  } else {
                    println!("Graceful shutdown request failed: {}", String::from_utf8_lossy(&output.stderr));
                  }
                },
                Err(e) => {
                  println!("Failed to send graceful shutdown request: {}", e);
                }
              }
            });

            // 等待优雅关闭尝试完成，但不超过3秒
            let _ = graceful_shutdown.join();

            // 等待一小段时间让服务器有机会关闭
            std::thread::sleep(Duration::from_millis(1500));

            // 然后强制终止进程
            if let Ok(mut backend_guard) = backend_child_clone.lock() {
              if let Some(mut child) = backend_guard.take() {
                // 首先尝试正常的kill
                match child.kill() {
                  Ok(_) => {
                    println!("Backend process terminated successfully");

                    // 额外的安全措施：使用taskkill强制终止可能残留的进程
                    std::thread::sleep(Duration::from_millis(500));
                    let _ = std::process::Command::new("taskkill")
                      .args(&["/F", "/IM", "kvs_backend.exe"])
                      .output();

                    // 强制终止监听5000端口的进程
                    let _ = std::process::Command::new("powershell")
                      .args(&["-Command", 
                        "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"])
                      .output();

                    println!("Additional cleanup completed");
                  },
                  Err(e) => {
                    eprintln!("Failed to terminate backend process: {}", e);

                    // 如果正常kill失败，直接使用taskkill
                    println!("Attempting forceful termination...");
                    let _ = std::process::Command::new("taskkill")
                      .args(&["/F", "/IM", "kvs_backend.exe"])
                      .output();

                    // 强制终止监听5000端口的进程
                    let _ = std::process::Command::new("powershell")
                      .args(&["-Command", 
                        "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"])
                      .output();
                  }
                }
              }
            }
          }
        }
        _ => {}
      }
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
