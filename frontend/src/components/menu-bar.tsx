import React, { useState, useEffect, useRef } from "react";
import { useTheme } from "./theme-provider";
import { Separator } from "./ui/separator";

interface MenuBarProps {
  onThemeChange: (theme: "light" | "dark") => void;
  onViewChange: (view: "k") => void;
  onShowStats: () => void;
  onShowAbout: () => void;
  onShowImport: () => void;
  onShowExport: () => void;
  onShowCleanup: () => void;
}

export function MenuBar({
  onThemeChange,
  onViewChange,
  onShowStats,
  onShowAbout,
  onShowImport,
  onShowExport,
  onShowCleanup,
}: MenuBarProps) {
  const { theme, setTheme } = useTheme();
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Handle click outside to close the menu
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpenMenu(null);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="flex items-center justify-between p-2 bg-secondary" ref={menuRef}>
      <div className="flex items-center">
        {/* Settings */}
        <div className="relative">
          <button
            className="px-3 py-1 rounded hover:bg-primary/10"
            onClick={() => setOpenMenu(openMenu === "settings" ? null : "settings")}
          >
            应用
          </button>
          {openMenu === "settings" && (
            <div className="absolute bg-background border rounded shadow-lg mt-1 z-10">
              {/*<button*/}
              {/*  className="block w-full text-left px-4 py-2 hover:bg-secondary whitespace-nowrap"*/}
              {/*  onClick={() => {*/}
              {/*    alert("设置功能");*/}
              {/*  }}*/}
              {/*>*/}
              {/*  设置*/}
              {/*</button>*/}
              <button
                className="block w-full text-left px-4 py-2 hover:bg-secondary whitespace-nowrap"
                onClick={() => {
                  onShowImport();
                  setOpenMenu(null);
                }}
              >
                数据导入
              </button>
              <button
                className="block w-full text-left px-4 py-2 hover:bg-secondary whitespace-nowrap"
                onClick={() => {
                  onShowExport();
                  setOpenMenu(null);
                }}
              >
                数据导出
              </button>
              <button
                className="block w-full text-left px-4 py-2 hover:bg-secondary whitespace-nowrap"
                onClick={() => {
                  onShowCleanup();
                  setOpenMenu(null);
                }}
              >
                数据清理
              </button>
            </div>
          )}
        </div>

        <Separator orientation="vertical" className="mx-2 h-6" />

        {/* Statistics */}
        <div className="relative">
          <button
            className="px-3 py-1 rounded hover:bg-primary/10"
            onClick={() => setOpenMenu(openMenu === "stats" ? null : "stats")}
          >
            统计
          </button>
          {openMenu === "stats" && (
            <div className="absolute bg-background border rounded shadow-lg mt-1 z-10">
              <button
                className="block w-full text-left px-4 py-2 hover:bg-secondary whitespace-nowrap"
                onClick={() => {
                  onShowStats();
                }}
              >
                KV统计
              </button>
            </div>
          )}
        </div>

        <Separator orientation="vertical" className="mx-2 h-6" />

        {/* View Options */}
        <div className="relative">
          <button 
            className="px-3 py-1 rounded hover:bg-primary/10"
            onClick={() => setOpenMenu(openMenu === "view" ? null : "view")}
          >
            视图
          </button>
          {openMenu === "view" && (
            <div className="absolute bg-background border rounded shadow-lg mt-1 z-10">
              <button
                className="block w-full text-left px-4 py-2 hover:bg-secondary whitespace-nowrap"
                onClick={() => {
                  onViewChange("k");
                }}
              >
                K视图探索
              </button>
            </div>
          )}
        </div>

        <Separator orientation="vertical" className="mx-2 h-6" />

        {/* Theme Mode Dropdown */}
        <div className="relative">
          <button 
            className="px-3 py-1 rounded hover:bg-primary/10"
            onClick={() => setOpenMenu(openMenu === "theme" ? null : "theme")}
          >
            主题
          </button>
          {openMenu === "theme" && (
            <div className="absolute bg-background border rounded shadow-lg mt-1 z-10">
              <button
                className={`block w-full text-left px-4 py-2 hover:bg-secondary whitespace-nowrap ${
                  theme === "light" ? "bg-secondary/50" : ""
                }`}
                onClick={() => {
                  setTheme("light");
                  onThemeChange("light");
                }}
              >
                浅色模式
              </button>
              <button
                className={`block w-full text-left px-4 py-2 hover:bg-secondary whitespace-nowrap ${
                  theme === "dark" ? "bg-secondary/50" : ""
                }`}
                onClick={() => {
                  setTheme("dark");
                  onThemeChange("dark");
                }}
              >
                深色模式
              </button>
            </div>
          )}
        </div>
      </div>

      {/* About */}
      <div>
        <button
          className="px-3 py-1 rounded hover:bg-primary/10"
          onClick={() => {
            onShowAbout();
          }}
        >
          关于
        </button>
      </div>
    </div>
  );
}
