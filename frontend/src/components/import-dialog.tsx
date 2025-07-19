import React, { useState, useEffect } from "react";
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel } from "./ui/alert-dialog";
import { Button } from "./ui/button";
import { Checkbox } from "./ui/checkbox";
import { ScrollArea } from "./ui/scroll-area";
import { Progress } from "./ui/progress";
import { useToast } from "./ui/use-toast";

interface ImportData {
  k: string;
  v: string[];
  create_at: string;
  valid: boolean;
  error?: string;
  index: number;
}

interface ImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onImportComplete?: () => void;
}

type ImportStage = "file-selection" | "data-preview" | "importing";

export function ImportDialog({ open, onOpenChange, onImportComplete }: ImportDialogProps) {
  const [stage, setStage] = useState<ImportStage>("file-selection");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importData, setImportData] = useState<ImportData[]>([]);
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importProgress, setImportProgress] = useState(0);
  const { toast } = useToast();

  // Reset state when dialog opens
  useEffect(() => {
    if (open) {
      setStage("file-selection");
      setSelectedFile(null);
      setImportData([]);
      setSelectedItems(new Set());
      setLoading(false);
      setImporting(false);
      setImportProgress(0);
    }
  }, [open]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.jsonl')) {
        toast({
          title: "文件格式错误",
          description: "请选择.jsonl格式的文件",
          variant: "destructive",
        });
        return;
      }
      setSelectedFile(file);
    }
  };

  const parseJsonlFile = async (file: File): Promise<ImportData[]> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string;
          const lines = content.split('\n').filter(line => line.trim());
          const parsedData: ImportData[] = [];

          lines.forEach((line, index) => {
            try {
              const data = JSON.parse(line);
              const importItem: ImportData = {
                k: data.k,
                v: data.v,
                create_at: data.create_at,
                valid: true,
                index: index,
              };

              // Validate data structure
              if (!data.k || typeof data.k !== 'string') {
                importItem.valid = false;
                importItem.error = "字段'k'缺失或类型错误";
              } else if (!data.v || !Array.isArray(data.v) || data.v.length === 0) {
                importItem.valid = false;
                importItem.error = "字段'v'缺失或不是非空数组";
              } else if (!data.v.every((item: any) => typeof item === 'string')) {
                importItem.valid = false;
                importItem.error = "字段'v'中包含非字符串元素";
              } else if (!data.create_at || typeof data.create_at !== 'string') {
                importItem.valid = false;
                importItem.error = "字段'create_at'缺失或类型错误";
              } else {
                // Validate timestamp format
                const timestamp = new Date(data.create_at);
                if (isNaN(timestamp.getTime())) {
                  importItem.valid = false;
                  importItem.error = "字段'create_at'时间格式无效";
                }
              }

              parsedData.push(importItem);
            } catch (parseError) {
              parsedData.push({
                k: "",
                v: [],
                create_at: "",
                valid: false,
                error: "JSON解析失败",
                index: index,
              });
            }
          });

          resolve(parsedData);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = () => reject(new Error("文件读取失败"));
      reader.readAsText(file);
    });
  };

  const handleNextStep = async () => {
    if (!selectedFile) {
      toast({
        title: "未选择文件",
        description: "请先选择要导入的文件",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const data = await parseJsonlFile(selectedFile);
      setImportData(data);
      
      // Auto-select valid items
      const validIndices = data.filter(item => item.valid).map(item => item.index);
      setSelectedItems(new Set(validIndices));
      
      setStage("data-preview");
    } catch (error) {
      toast({
        title: "文件解析失败",
        description: error instanceof Error ? error.message : "未知错误",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const validIndices = importData.filter(item => item.valid).map(item => item.index);
      setSelectedItems(new Set(validIndices));
    } else {
      setSelectedItems(new Set());
    }
  };

  const handleSelectItem = (index: number, checked: boolean) => {
    const newSelected = new Set(selectedItems);
    if (checked) {
      newSelected.add(index);
    } else {
      newSelected.delete(index);
    }
    setSelectedItems(newSelected);
  };

  const handleImport = async () => {
    if (selectedItems.size === 0) {
      toast({
        title: "未选择数据",
        description: "请选择要导入的KV数据",
        variant: "destructive",
      });
      return;
    }

    setStage("importing");
    setImporting(true);
    setImportProgress(0);

    try {
      const selectedData = importData
        .filter(item => selectedItems.has(item.index) && item.valid)
        .map(item => ({
          k: item.k,
          v: item.v,
          create_at: item.create_at,
        }));

      const response = await fetch('http://localhost:5000/api/v1/kv/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: selectedData
        }),
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        setImportProgress(100);
        toast({
          title: "导入完成",
          description: `成功导入 ${result.data.imported_count} 条KV数据`,
        });
        
        // Call completion callback
        if (onImportComplete) {
          onImportComplete();
        }
        
        // Close dialog after a short delay
        setTimeout(() => {
          onOpenChange(false);
        }, 1500);
      } else {
        throw new Error(result.message || "导入失败");
      }
    } catch (error) {
      toast({
        title: "导入失败",
        description: error instanceof Error ? error.message : "网络错误",
        variant: "destructive",
      });
      setStage("data-preview");
    } finally {
      setImporting(false);
    }
  };

  const truncateText = (text: string, maxLength: number = 50) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  const validCount = importData.filter(item => item.valid).length;
  const invalidCount = importData.length - validCount;
  const allValidSelected = validCount > 0 && selectedItems.size === validCount;
  const someSelected = selectedItems.size > 0 && selectedItems.size < validCount;

  const renderFileSelection = () => (
    <div className="flex-1 flex flex-col items-center justify-center p-8">
      <div className="text-center mb-6">
        <h3 className="text-lg font-medium mb-2">选择导入文件</h3>
        <p className="text-muted-foreground">请选择JSONL格式的KV数据文件</p>
      </div>
      
      <div className="w-full max-w-md">
        <input
          type="file"
          accept=".jsonl"
          onChange={handleFileSelect}
          className="w-full p-3 border border-dashed border-gray-300 rounded-lg text-center cursor-pointer hover:border-primary"
        />
        
        {selectedFile && (
          <div className="mt-4 p-3 bg-muted rounded-lg">
            <p className="text-sm font-medium">已选择文件:</p>
            <p className="text-sm text-muted-foreground">{selectedFile.name}</p>
            <p className="text-xs text-muted-foreground">
              大小: {(selectedFile.size / 1024).toFixed(2)} KB
            </p>
          </div>
        )}
      </div>
    </div>
  );

  const renderDataPreview = () => (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Selection controls */}
      <div className="flex items-center gap-4 p-4 border-b">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="select-all"
            checked={someSelected ? "indeterminate" : allValidSelected}
            onCheckedChange={handleSelectAll}
            disabled={loading}
          />
          <label htmlFor="select-all" className="text-sm font-medium">
            全选 ({selectedItems.size}/{validCount})
          </label>
        </div>
        <div className="text-sm text-muted-foreground">
          有效数据: {validCount} 条
        </div>
        {invalidCount > 0 && (
          <div className="text-sm text-red-500">
            无效数据: {invalidCount} 条
          </div>
        )}
      </div>

      {/* Data list */}
      <ScrollArea className="flex-1">
        <div className="p-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-muted-foreground">解析中...</div>
            </div>
          ) : importData.length === 0 ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-muted-foreground">暂无数据</div>
            </div>
          ) : (
            <div className="space-y-2">
              {importData.map((item) => (
                <div
                  key={item.index}
                  className={`flex items-center space-x-3 p-3 border rounded-lg ${
                    item.valid ? "hover:bg-muted/50" : "bg-red-50 border-red-200"
                  }`}
                >
                  <Checkbox
                    id={`item-${item.index}`}
                    checked={selectedItems.has(item.index)}
                    onCheckedChange={(checked) => handleSelectItem(item.index, checked as boolean)}
                    disabled={!item.valid}
                  />
                  <div className="flex-1">
                    <div className={`font-medium ${item.valid ? "" : "text-red-600"}`}>
                      {item.valid ? truncateText(item.k, 50) : `行 ${item.index + 1}: ${item.error}`}
                    </div>
                    {item.valid && (
                      <div className="text-sm text-muted-foreground">
                        {item.v.length} 个值 • {new Date(item.create_at).toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );

  const renderImporting = () => (
    <div className="flex-1 flex flex-col items-center justify-center p-8">
      <div className="text-center mb-6">
        <h3 className="text-lg font-medium mb-2">正在导入数据</h3>
        <p className="text-muted-foreground">请稍候，正在处理您的数据...</p>
      </div>
      
      <div className="w-full max-w-md">
        <Progress value={importProgress} className="w-full" />
        <p className="text-sm text-muted-foreground text-center mt-2">
          {importProgress}%
        </p>
      </div>
    </div>
  );

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="max-w-full max-h-full w-screen h-screen m-0 rounded-none">
        <AlertDialogHeader>
          <AlertDialogTitle>
            {stage === "file-selection" && "KV数据导入"}
            {stage === "data-preview" && "数据预览"}
            {stage === "importing" && "导入进度"}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {stage === "file-selection" && "选择要导入的JSONL格式文件"}
            {stage === "data-preview" && "选择要导入的KV数据，无效数据将被跳过"}
            {stage === "importing" && "正在导入选中的KV数据"}
          </AlertDialogDescription>
        </AlertDialogHeader>

        {stage === "file-selection" && renderFileSelection()}
        {stage === "data-preview" && renderDataPreview()}
        {stage === "importing" && renderImporting()}

        <AlertDialogFooter>
          {stage === "file-selection" && (
            <>
              <AlertDialogCancel disabled={loading}>取消</AlertDialogCancel>
              <Button onClick={handleNextStep} disabled={!selectedFile || loading}>
                {loading ? "解析中..." : "下一步"}
              </Button>
            </>
          )}
          {stage === "data-preview" && (
            <>
              <AlertDialogCancel disabled={importing}>取消</AlertDialogCancel>
              <Button onClick={handleImport} disabled={selectedItems.size === 0 || importing}>
                导入 ({selectedItems.size})
              </Button>
            </>
          )}
          {stage === "importing" && (
            <AlertDialogCancel disabled={importing}>关闭</AlertDialogCancel>
          )}
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}