import { useState, useEffect } from "react";
import { ThemeProvider } from "./components/theme-provider";
import { MenuBar } from "./components/menu-bar";
import { TabLayout } from "./components/tab-layout";
import { getCurrentTheme, setThemeMode } from "./services/theme-service";
import { getKVStats, KVStatsData } from "./services/kv-service";
import { getVersion } from "@tauri-apps/api/app";
import { appWindow } from "@tauri-apps/api/window";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "./components/ui/alert-dialog";
import { Toaster } from "./components/ui/toaster";
import { useToast } from "./hooks/use-toast";
import { DebugLogs } from "./components/debug-logs";
import { logger } from "./utils/logger";
import { Alert, AlertDescription, AlertTitle } from "./components/ui/alert";
import { ExportDialog } from "./components/export-dialog";
import { ImportDialog } from "./components/import-dialog";
import { CleanupDialog } from "./components/cleanup-dialog";
import { KViewDialog } from "./components/k-view-dialog";

function App() {
  const [currentView, setCurrentView] = useState<"k">("k");
  const [showAboutDialog, setShowAboutDialog] = useState(false);
  const [showStatsDialog, setShowStatsDialog] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showCleanupDialog, setShowCleanupDialog] = useState(false);
  const [showKViewDialog, setShowKViewDialog] = useState(false);
  const [statsData, setStatsData] = useState<KVStatsData | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [initialTheme, setInitialTheme] = useState<"light" | "dark" | null>(null);
  const [appVersion, setAppVersion] = useState<string>("0.1.0");
  const [backendConnected, setBackendConnected] = useState<boolean>(true);
  const { toast } = useToast();

  // Fetch the current theme from the API on application startup
  useEffect(() => {
    const fetchTheme = async () => {
      try {
        // Add a timeout to prevent hanging indefinitely
        const themePromise = getCurrentTheme();
        const timeoutPromise = new Promise<"light" | "dark">((resolve) => {
          setTimeout(() => {
            console.warn("Theme fetch timed out, using default light theme");
            resolve("light");
          }, 3000); // 3 second timeout
        });

        // Race the theme fetch against the timeout
        const theme = await Promise.race([themePromise, timeoutPromise]);
        setInitialTheme(theme);

        // Check if we're using mock data by making a test API call
        try {
          const response = await fetch("http://127.0.0.1:5000/api/v1/health", {
            method: 'GET',
            signal: AbortSignal.timeout(1000) // 1 second timeout
          });
          setBackendConnected(response.ok);
        } catch (error) {
          // If we can't connect to the backend, set backendConnected to false
          setBackendConnected(false);
        }
      } catch (error) {
        console.error("Failed to fetch theme:", error);
        // Set a default theme if there's an error
        setInitialTheme("light");
        setBackendConnected(false);
      }
    };

    fetchTheme();
  }, []);

  // Fetch the application version on startup
  useEffect(() => {
    const fetchVersion = async () => {
      try {
        const version = await getVersion();
        setAppVersion(version);
      } catch (error) {
        console.error("Failed to get application version:", error);
      }
    };

    fetchVersion();
  }, []);

  // Set up cleanup for logger when window is closed
  useEffect(() => {
    const unlisten = appWindow.onCloseRequested(async (event) => {
      // Prevent the default close behavior
      event.preventDefault();

      try {
        // Clean up logger resources
        await logger.cleanup();
        console.log("Logger cleanup completed");
      } catch (error) {
        console.error("Error during logger cleanup:", error);
      }

      // Explicitly close the window after cleanup
      await appWindow.close();
    });

    // Clean up the event listener when component unmounts
    return () => {
      unlisten.then(unlistenFn => unlistenFn());
    };
  }, []);

  const handleThemeChange = async (theme: "light" | "dark") => {
    console.log(`Theme changed to ${theme}`);
    // Update the theme in the backend via API
    await setThemeMode(theme);
  };

  const handleViewChange = (view: "k") => {
    setCurrentView(view);
    setShowKViewDialog(true);
    console.log(`View changed to ${view}`);
  };

  const handleShowStats = async () => {
    setStatsLoading(true);
    setShowStatsDialog(true);

    try {
      const stats = await getKVStats();
      setStatsData(stats);
      console.log("[DEBUG_LOG] KV Statistics fetched:", stats);
    } catch (error) {
      console.error("[DEBUG_LOG] Error fetching KV statistics:", error);
      toast({
        title: "获取统计数据失败",
        description: "无法获取KV统计数据，请检查后端连接",
        variant: "destructive",
      });
      setStatsData(null);
    } finally {
      setStatsLoading(false);
    }
  };

  const handleShowAbout = () => {
    setShowAboutDialog(true);
  };

  const handleCloseAbout = () => {
    setShowAboutDialog(false);
  };

  const handleShowExport = () => {
    setShowExportDialog(true);
  };

  const handleShowImport = () => {
    setShowImportDialog(true);
  };

  const handleShowCleanup = () => {
    setShowCleanupDialog(true);
  };

  // Only render the app once we've fetched the initial theme
  if (initialTheme === null) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-white dark:bg-cyan-900">
        <div className="w-20 h-20 mb-6 bg-cyan-500 rounded-full flex items-center justify-center animate-pulse">
          <span className="text-3xl font-bold text-yellow-200">KVs</span>
        </div>
        <h1 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">Memory KV for You</h1>
        <div className="flex space-x-2 mt-2">
          <div className="w-3 h-3 bg-cyan-500 rounded-full animate-bounce"></div>
          <div className="w-3 h-3 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-3 h-3 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">Loading application...</p>
      </div>
    );
  }

  return (
    <ThemeProvider defaultTheme={initialTheme}>
      <div className="flex flex-col h-screen">
        <MenuBar
          onThemeChange={handleThemeChange}
          onViewChange={handleViewChange}
          onShowStats={handleShowStats}
          onShowAbout={handleShowAbout}
          onShowImport={handleShowImport}
          onShowExport={handleShowExport}
          onShowCleanup={handleShowCleanup}
        />

        {!backendConnected && (
          <Alert variant="destructive" className="m-2">
            <AlertTitle>后端服务未连接</AlertTitle>
            <AlertDescription>
              无法连接到后端服务器。应用程序将以有限功能运行。
            </AlertDescription>
          </Alert>
        )}

        <main className="flex-1 w-full overflow-y-auto">
          <TabLayout />
        </main>
      </div>

      <AlertDialog open={showAboutDialog} onOpenChange={setShowAboutDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>关于</AlertDialogTitle>
            <AlertDialogDescription>
              KVs - 一个简单的键值存储应用 - v.{appVersion}
            </AlertDialogDescription>
          </AlertDialogHeader>

          <div className="py-4">
            <DebugLogs />
          </div>

          <AlertDialogFooter>
            <AlertDialogAction onClick={handleCloseAbout}>确定</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showStatsDialog} onOpenChange={setShowStatsDialog}>
        <AlertDialogContent className="max-w-2xl">
          <AlertDialogHeader>
            <AlertDialogTitle>KV统计</AlertDialogTitle>
            <AlertDialogDescription>
              键值对存储统计信息
            </AlertDialogDescription>
          </AlertDialogHeader>

          <div className="py-4">
            {statsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <span className="ml-2">加载统计数据中...</span>
              </div>
            ) : statsData ? (
              <div className="space-y-6">
                {/* Basic Statistics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-secondary/20 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold text-primary">唯一K数量</h3>
                    <p className="text-2xl font-bold">{statsData.unique_k_count}</p>
                  </div>
                  <div className="bg-secondary/20 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold text-primary">V总数量</h3>
                    <p className="text-2xl font-bold">{statsData.total_v_count}</p>
                  </div>
                </div>

                {/* V Distribution Chart */}
                <div className="bg-secondary/10 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-primary mb-4">K-V关系分布</h3>
                  <div className="space-y-2">
                    {Object.entries(statsData.v_distribution).map(([vCount, kCount]) => (
                      <div key={vCount} className="flex items-center justify-between">
                        <span className="text-sm">
                          {vCount === '5+' ? '5个以上V的K' : `${vCount}个V的K`}
                        </span>
                        <div className="flex items-center space-x-2 flex-1 mx-4">
                          <div className="flex-1 bg-secondary/30 rounded-full h-4 relative">
                            <div 
                              className="bg-primary h-4 rounded-full transition-all duration-300"
                              style={{ 
                                width: statsData.unique_k_count > 0 
                                  ? `${(kCount / statsData.unique_k_count) * 100}%` 
                                  : '0%' 
                              }}
                            />
                          </div>
                          <span className="text-sm font-medium w-8 text-right">{kCount}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                无法加载统计数据
              </div>
            )}
          </div>

          <AlertDialogFooter>
            <AlertDialogAction onClick={() => setShowStatsDialog(false)}>关闭</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <ExportDialog 
        open={showExportDialog} 
        onOpenChange={setShowExportDialog} 
      />

      <ImportDialog 
        open={showImportDialog} 
        onOpenChange={setShowImportDialog} 
      />

      <CleanupDialog 
        open={showCleanupDialog} 
        onOpenChange={setShowCleanupDialog} 
      />

      <KViewDialog 
        open={showKViewDialog} 
        onOpenChange={setShowKViewDialog} 
      />
      
      <Toaster />
    </ThemeProvider>
  );
}

export default App;
