import React, { useState, useEffect } from "react";
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel } from "./ui/alert-dialog";
import { Button } from "./ui/button";
import { Checkbox } from "./ui/checkbox";
import { ScrollArea } from "./ui/scroll-area";
import { useToast } from "./ui/use-toast";

interface KVData {
  id: number;
  key: string;
  vals: string[];
  created_at: string;
  updated_at: string | null;
}

interface CleanupDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCleanupComplete?: () => void;
}

export function CleanupDialog({ open, onOpenChange, onCleanupComplete }: CleanupDialogProps) {
  const [kvData, setKvData] = useState<KVData[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [hoveredKey, setHoveredKey] = useState<number | null>(null);
  const { toast } = useToast();

  // Fetch all KV data when dialog opens
  useEffect(() => {
    if (open) {
      fetchKVData();
      setSelectedKeys(new Set()); // Reset selection when dialog opens
    }
  }, [open]);

  // Track mouse position for tooltip positioning
  const handleMouseMove = (event: React.MouseEvent) => {
    setMousePosition({ x: event.clientX, y: event.clientY });
  };

  const fetchKVData = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/v1/kv');
      const result = await response.json();
      
      if (result.status === 'success') {
        setKvData(result.data);
      } else {
        toast({
          title: "获取数据失败",
          description: result.message || "无法获取KV数据",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "网络错误",
        description: "无法连接到服务器",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedKeys(new Set(kvData.map(kv => kv.id)));
    } else {
      setSelectedKeys(new Set());
    }
  };

  const handleSelectKey = (keyId: number, checked: boolean) => {
    const newSelected = new Set(selectedKeys);
    if (checked) {
      newSelected.add(keyId);
    } else {
      newSelected.delete(keyId);
    }
    setSelectedKeys(newSelected);
  };

  const handleBatchDelete = async () => {
    if (selectedKeys.size === 0) {
      toast({
        title: "未选择数据",
        description: "请选择要删除的KV数据",
        variant: "destructive",
      });
      return;
    }

    setDeleting(true);
    try {
      const response = await fetch('http://localhost:5000/api/v1/kv/batch-delete', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          key_ids: Array.from(selectedKeys)
        }),
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        toast({
          title: "清理完成",
          description: `成功删除 ${result.deleted_count} 条KV数据`,
        });
        
        // Refresh the data
        await fetchKVData();
        setSelectedKeys(new Set());
        
        // Call completion callback
        if (onCleanupComplete) {
          onCleanupComplete();
        }
      } else {
        toast({
          title: "删除失败",
          description: result.message || "删除操作失败",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "网络错误",
        description: "无法连接到服务器",
        variant: "destructive",
      });
    } finally {
      setDeleting(false);
    }
  };

  const truncateText = (text: string, maxLength: number = 50) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  const getTooltipContent = (vals: string[]) => {
    const displayVals = vals.slice(0, 3); // Show first 3 values
    return (
      <div className="max-w-xs">
        <div className="font-semibold mb-1">前3条V值:</div>
        {displayVals.map((val, index) => (
          <div key={index} className="text-sm mb-1">
            {index + 1}. {truncateText(val, 30)}
          </div>
        ))}
        {vals.length > 3 && (
          <div className="text-xs text-muted-foreground mt-1">
            还有 {vals.length - 3} 条数据...
          </div>
        )}
      </div>
    );
  };

  const allSelected = kvData.length > 0 && selectedKeys.size === kvData.length;
  const someSelected = selectedKeys.size > 0 && selectedKeys.size < kvData.length;

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="max-w-full max-h-full w-screen h-screen m-0 rounded-none">
        <AlertDialogHeader>
          <AlertDialogTitle>KV数据清理</AlertDialogTitle>
          <AlertDialogDescription>
            选择要删除的KV数据。鼠标悬停在K值上可查看前3条V值。
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="flex-1 flex flex-col min-h-0">
          {/* Selection controls */}
          <div className="flex items-center gap-4 p-4 border-b">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="select-all"
                checked={someSelected ? "indeterminate" : allSelected}
                onCheckedChange={handleSelectAll}
                disabled={loading}
              />
              <label htmlFor="select-all" className="text-sm font-medium">
                全选 ({selectedKeys.size}/{kvData.length})
              </label>
            </div>
            <div className="text-sm text-muted-foreground">
              已选择 {selectedKeys.size} 条数据
            </div>
          </div>

          {/* KV data list */}
          <ScrollArea className="flex-1">
            <div className="p-4">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="text-muted-foreground">加载中...</div>
                </div>
              ) : kvData.length === 0 ? (
                <div className="flex items-center justify-center py-8">
                  <div className="text-muted-foreground">暂无KV数据</div>
                </div>
              ) : (
                <div className="space-y-2">
                  {kvData.map((kv) => (
                    <div
                      key={kv.id}
                      className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-muted/50"
                    >
                      <Checkbox
                        id={`kv-${kv.id}`}
                        checked={selectedKeys.has(kv.id)}
                        onCheckedChange={(checked) => handleSelectKey(kv.id, checked as boolean)}
                      />
                      <div className="flex-1">
                        <div 
                          className="font-medium cursor-help hover:text-primary relative"
                          onMouseMove={handleMouseMove}
                          onMouseEnter={() => setHoveredKey(kv.id)}
                          onMouseLeave={() => setHoveredKey(null)}
                        >
                          {truncateText(kv.key, 50)}
                          {hoveredKey === kv.id && (
                            <div 
                              className="fixed z-50 bg-primary text-primary-foreground px-3 py-1.5 text-xs rounded-md shadow-lg max-w-sm pointer-events-none"
                              style={{
                                left: mousePosition.x + 15, // 15px to the right of cursor
                                top: mousePosition.y - 10,  // Slightly above cursor
                              }}
                            >
                              {getTooltipContent(kv.vals)}
                            </div>
                          )}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {kv.vals.length} 个值 • 创建于 {new Date(kv.created_at).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </ScrollArea>
        </div>

        <AlertDialogFooter>
          <AlertDialogCancel disabled={deleting}>取消</AlertDialogCancel>
          <Button
            onClick={handleBatchDelete}
            disabled={selectedKeys.size === 0 || deleting}
            variant="destructive"
          >
            {deleting ? "删除中..." : `批量清理 (${selectedKeys.size})`}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}