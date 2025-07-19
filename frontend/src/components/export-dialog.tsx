import React, { useState, useEffect } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "./ui/alert-dialog";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { useToast } from "./ui/use-toast";
import { save } from "@tauri-apps/api/dialog";
import { writeTextFile } from "@tauri-apps/api/fs";

interface ExportStats {
  k_count: number;
  v_count: number;
  kv_pairs_count: number;
}

interface ExportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ExportDialog({ open, onOpenChange }: ExportDialogProps) {
  const [stats, setStats] = useState<ExportStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const { toast } = useToast();

  // Fetch export statistics when dialog opens
  useEffect(() => {
    if (open) {
      fetchExportStats();
    }
  }, [open]);

  const fetchExportStats = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:5000/api/v1/kv/export/stats");
      const data = await response.json();
      
      if (data.status === "success") {
        setStats(data.data);
      } else {
        toast({
          title: "获取统计数据失败",
          description: data.message || "无法获取导出统计数据",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Failed to fetch export stats:", error);
      toast({
        title: "网络错误",
        description: "无法连接到服务器获取统计数据",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      // Use Tauri's save dialog to let user choose export location
      const filePath = await save({
        filters: [
          {
            name: "JSONL Files",
            extensions: ["jsonl"]
          }
        ],
        defaultPath: "kv_export.jsonl"
      });

      if (!filePath) {
        // User cancelled the dialog
        return;
      }

      setIsExporting(true);

      // Fetch export data from backend
      const response = await fetch("http://localhost:5000/api/v1/kv/export");
      const data = await response.json();

      if (data.status === "success") {
        // Convert data to JSONL format
        const jsonlContent = data.data
          .map((record: any) => JSON.stringify(record))
          .join("\n");

        // Write file using Tauri
        await writeTextFile(filePath, jsonlContent);

        toast({
          title: "导出成功",
          description: `已成功导出 ${data.count} 条KV记录到 ${filePath}`,
        });

        onOpenChange(false);
      } else {
        toast({
          title: "导出失败",
          description: data.message || "导出过程中发生错误",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Export failed:", error);
      toast({
        title: "导出失败",
        description: "导出过程中发生错误，请重试",
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="max-w-md">
        <AlertDialogHeader>
          <AlertDialogTitle>数据导出</AlertDialogTitle>
          <AlertDialogDescription>
            将当前存储的KV数据导出为JSONL格式文件
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="py-4">
          {isLoading ? (
            <div className="text-center text-muted-foreground">
              正在获取统计数据...
            </div>
          ) : stats ? (
            <div className="space-y-3">
              <div className="text-sm font-medium">待导出数据统计：</div>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="space-y-1">
                  <div className="text-2xl font-bold text-primary">
                    {stats.k_count}
                  </div>
                  <Label className="text-xs text-muted-foreground">
                    K数量
                  </Label>
                </div>
                <div className="space-y-1">
                  <div className="text-2xl font-bold text-primary">
                    {stats.v_count}
                  </div>
                  <Label className="text-xs text-muted-foreground">
                    V数量
                  </Label>
                </div>
                <div className="space-y-1">
                  <div className="text-2xl font-bold text-primary">
                    {stats.kv_pairs_count}
                  </div>
                  <Label className="text-xs text-muted-foreground">
                    KV对数量
                  </Label>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-muted-foreground">
              无法获取统计数据
            </div>
          )}
        </div>

        <AlertDialogFooter>
          <AlertDialogCancel disabled={isExporting}>
            取消
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={handleExport}
            disabled={isLoading || !stats || isExporting}
          >
            {isExporting ? "导出中..." : "导出"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}