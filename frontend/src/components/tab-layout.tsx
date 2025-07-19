import React, {useRef, useState, useEffect} from "react";
import {createKV, deleteKV, KVData, searchKV, updateKV} from "../utils/api";
import {Input} from "./ui/input";
import {Button} from "./ui/button";
import {ScrollArea} from "./ui/scroll-area";
import {Label} from "./ui/label";
import {Plus, Search, Trash2} from "lucide-react";
import {useToast} from "../hooks/use-toast";
import {RadioGroup, RadioGroupItem} from "./ui/radio-group";
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

export function TabLayout() {
  const [activeTab, setActiveTab] = useState<"tab1" | "tab2">("tab1");
  const [keyValue, setKeyValue] = useState<string>("");
  const [valInputs, setValInputs] = useState<string[]>([""]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchMode, setSearchMode] = useState<string>("key"); // Default to key search mode
  const [searchResults, setSearchResults] = useState<KVData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState<boolean>(false);
  const [keyToDelete, setKeyToDelete] = useState<number | null>(null);
  const [isEditingKV, setIsEditingKV] = useState<boolean>(false);
  const [editingKV, setEditingKV] = useState<KVData | null>(null);
  const [editKeyValue, setEditKeyValue] = useState<string>("");
  const [editValInputs, setEditValInputs] = useState<string[]>([""]);
  const [scrollPosition, setScrollPosition] = useState<number>(0);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Restore scroll position when tab becomes active or search results change
  useEffect(() => {
    if (activeTab === "tab2" && scrollAreaRef.current) {
      console.log('scroll to ' + scrollPosition);
      const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (viewport) {
        viewport.scrollTop = scrollPosition;
      }
    }
  }, [activeTab, searchResults, scrollPosition]);

  // Attach scroll event listener to viewport
  useEffect(() => {
    if (activeTab === "tab2" && scrollAreaRef.current) {
      const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (viewport) {
        const handleScroll = (event: Event) => {
          const target = event.target as HTMLDivElement;
          console.log('scroll ' + target.scrollTop);
          setScrollPosition(target.scrollTop);
        };

        viewport.addEventListener('scroll', handleScroll);
        return () => {
          viewport.removeEventListener('scroll', handleScroll);
        };
      }
    }
  }, [activeTab, scrollAreaRef.current]);

  const handleAddValInput = () => {
    setValInputs([...valInputs, ""]);
  };

  const handleValInputChange = (index: number, value: string) => {
    const newValInputs = [...valInputs];
    newValInputs[index] = value;
    setValInputs(newValInputs);
  };

  const handleResetKV = () => {
    setKeyValue("");
    setValInputs([""]);
  }

  const handleReset = () => {
    toast({
      title: "已重置",
      description: "再来一次KV-Do吧!",
    });
    handleResetKV();
  };

  const handleCreateKV = async () => {
    if (!keyValue.trim()) {
      toast({
        title: "错误",
        description: "Key不能为空",
        variant: "destructive",
      });
      return;
    }

    // Filter out empty val inputs
    const filteredVals = valInputs.filter(val => val.trim() !== "");

    if (filteredVals.length === 0) {
      toast({
        title: "错误",
        description: "至少需要一个Val值",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await createKV(keyValue, filteredVals);
      if (response.status === "success") {
        toast({
          title: "已保存",
          description: "KV数据已保存",
        });
        handleResetKV();
      } else {
        toast({
          title: "错误",
          description: response.message || "保存失败",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "错误",
        description: `保存失败: ${error}`,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast({
        title: "错误",
        description: "搜索关键词不能为空",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    // Reset scroll position when performing a new search
    setScrollPosition(0);
    try {
      const response = await searchKV(searchQuery, searchMode);
      if (response.status === "success") {
        setSearchResults(response.data);
        toast({
          title: "搜索完成",
          description: `找到 ${response.data.length} 条结果`,
        });
      } else {
        toast({
          title: "错误",
          description: response.message || "搜索失败",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "错误",
        description: `搜索失败: ${error}`,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmDelete = (keyId: number) => {
    setKeyToDelete(keyId);
    setShowDeleteDialog(true);
  };

  const handleDeleteKV = async () => {
    if (keyToDelete === null) return;

    setShowDeleteDialog(false);
    setIsLoading(true);
    try {
      const response = await deleteKV(keyToDelete);
      if (response.status === "success") {
        // Remove the deleted item from search results
        setSearchResults(prevResults => prevResults.filter(item => item.id !== keyToDelete));
        toast({
          title: "成功",
          description: "KV数据已删除",
        });
      } else {
        toast({
          title: "错误",
          description: response.message || "删除失败",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "错误",
        description: `删除失败: ${error}`,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
      setKeyToDelete(null);
    }
  };

  const handleEditKV = (kv: KVData) => {
    // Save current scroll position before entering edit mode
    if (scrollAreaRef.current) {
      const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (viewport) {
        setScrollPosition(viewport.scrollTop);
        console.log('Saved scroll position before edit: ' + viewport.scrollTop);
      }
    }
    
    setEditingKV(kv);
    setEditKeyValue(kv.key);
    setEditValInputs(kv.vals.length > 0 ? [...kv.vals] : [""]);
    setIsEditingKV(true);
  };

  const handleAddEditValInput = () => {
    setEditValInputs([...editValInputs, ""]);
  };

  const handleEditValInputChange = (index: number, value: string) => {
    const newEditValInputs = [...editValInputs];
    newEditValInputs[index] = value;
    setEditValInputs(newEditValInputs);
  };

  const handleSaveEditKV = async () => {
    if (!editingKV) return;

    if (!editKeyValue.trim()) {
      toast({
        title: "错误",
        description: "Key不能为空",
        variant: "destructive",
      });
      return;
    }

    // Filter out empty val inputs
    const filteredVals = editValInputs.filter(val => val.trim() !== "");

    if (filteredVals.length === 0) {
      toast({
        title: "错误",
        description: "至少需要一个Val值",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await updateKV(editingKV.id, editKeyValue, filteredVals);
      if (response.status === "success") {
        // Update the item in search results
        setSearchResults(prevResults =>
          prevResults.map(item =>
            item.id === editingKV.id
              ? { ...item, key: editKeyValue, vals: filteredVals, updated_at: new Date().toISOString() }
              : item
          )
        );
        toast({
          title: "成功",
          description: "KV数据已更新",
        });
        setIsEditingKV(false);
        setEditingKV(null);
        setEditKeyValue("");
        setEditValInputs([""]);
        
        // Restore scroll position after returning from edit mode
        setTimeout(() => {
          if (scrollAreaRef.current) {
            const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
            if (viewport) {
              viewport.scrollTop = scrollPosition;
              console.log('Restored scroll position after save: ' + scrollPosition);
            }
          }
        }, 0);
      } else {
        toast({
          title: "错误",
          description: response.message || "更新失败",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "错误",
        description: `更新失败: ${error}`,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelEditKV = () => {
    setIsEditingKV(false);
    setEditingKV(null);
    setEditKeyValue("");
    setEditValInputs([""]);
    
    // Restore scroll position after returning from edit mode
    setTimeout(() => {
      if (scrollAreaRef.current) {
        const viewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
        if (viewport) {
          viewport.scrollTop = scrollPosition;
          console.log('Restored scroll position after cancel: ' + scrollPosition);
        }
      }
    }, 0);
  };

  return (
    <div className="flex flex-col h-full">
      {!isEditingKV ? (
        <>
          {/* Tab Headers */}
          <div className="flex w-full">
            <button
              className={`flex-1 py-2 text-center ${
                activeTab === "tab1"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary hover:bg-secondary/80"
              }`}
              onClick={() => setActiveTab("tab1")}
            >
              快记
            </button>
            <button
              className={`flex-1 py-2 text-center ${
                activeTab === "tab2"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary hover:bg-secondary/80"
              }`}
              onClick={() => setActiveTab("tab2")}
            >
              快搜
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 p-4 overflow-hidden w-full">
            {activeTab === "tab1" && (
              <div className="flex flex-col h-full space-y-4">
                {/* Key Input */}
                <div className="flex items-center space-x-2">
                  <span className="min-w-16 text-right">Key with </span>
                  <Input
                    value={keyValue}
                    onChange={(e) => setKeyValue(e.target.value)}
                    className="flex-1"
                    disabled={isLoading}
                  />
                </div>

                {/* Add Button */}
                <div className="flex justify-center">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={handleAddValInput}
                    className="rounded-full"
                    disabled={isLoading}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>

                {/* Scroll Area with Val Inputs */}
                <div className="flex-1 overflow-y-auto">
                  <ScrollArea className="flex-1 border rounded-md p-4">
                    <div className="flex flex-col space-y-4">
                      {valInputs.map((val, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <span className="min-w-16 text-right">Val_{index} for</span>
                            <Input
                                value={val}
                                onChange={(e) => handleValInputChange(index, e.target.value)}
                                className="flex-1"
                                disabled={isLoading}
                            />
                          </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-between">
                  <Button onClick={handleReset} disabled={isLoading}>恢复默认</Button>
                  <Button onClick={handleCreateKV} disabled={isLoading}>
                    {isLoading ? "处理中..." : "KVs-Do!"}
                  </Button>
                </div>
              </div>
            )}

            {activeTab === "tab2" && (
              <div className="flex flex-col h-full space-y-4">
                {/* Search Mode Selection */}
                <div className="flex flex-row space-x-6">
                  <RadioGroup 
                    value={searchMode} 
                    onValueChange={setSearchMode}
                    className="flex flex-row space-x-6"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="key" id="key-search" />
                      <Label htmlFor="key-search">K搜索</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="value" id="value-search" />
                      <Label htmlFor="value-search">V搜索</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="mixed" id="mixed-search" />
                      <Label htmlFor="mixed-search">KV混合搜索</Label>
                    </div>
                  </RadioGroup>
                </div>

                {/* Search Input */}
                <div className="flex items-center space-x-2">
                  <Input
                    ref={searchInputRef}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !isLoading) {
                        handleSearch();
                        // Set a 2-second timer to auto-focus the input field
                        setTimeout(() => {
                          if (searchInputRef.current) {
                            searchInputRef.current.focus();
                          }
                        }, 2000);
                      }
                    }}
                    placeholder="输入搜索关键词..."
                    className="flex-1"
                    disabled={isLoading}
                  />
                  <Button
                    onClick={handleSearch}
                    disabled={isLoading}
                    className="flex items-center gap-2"
                  >
                    <Search className="h-4 w-4" />
                    {isLoading ? "搜索中..." : "搜索"}
                  </Button>
                </div>

                {/* Search Results */}
                <div className="flex-1 overflow-y-auto">
                  <ScrollArea
                    ref={scrollAreaRef}
                    className="flex-1 border rounded-md p-4 h-full"
                  >
                    <div className="h-full">
                      {searchResults.length === 0 ? (
                        <div className="flex items-center justify-center h-full text-muted-foreground">
                          {isLoading ? "搜索中..." : "无搜索结果"}
                        </div>
                      ) : (
                        <div className="flex flex-col space-y-6 w-full">
                          {searchResults.map((result) => (
                              <div key={result.id} className="border-b pb-4 relative">
                                <div className="flex flex-row justify-between space-x-4 w-full">
                                  <div
                                      className="min-w-0 flex-1 cursor-pointer hover:bg-secondary/20 p-1 rounded transition-colors"
                                      onClick={() => handleEditKV(result)}
                                  >
                                    <h3 className="text-lg font-semibold truncate pr-2">{result.key}</h3>
                                  </div>
                                  <Button
                                      variant="ghost"
                                      size="icon"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleConfirmDelete(result.id);
                                      }}
                                      disabled={isLoading}
                                  >
                                    <Trash2 className="h-4 w-2 text-destructive" />
                                  </Button>
                                </div>
                                <div
                                    className="space-y-2 hover:bg-secondary/10 p-1 rounded transition-colors pr-16"
                                >
                                  {result.vals.slice(0, 3).map((val, index) => (
                                      <div key={index} className="bg-secondary/30 p-2 rounded truncate">
                                        {val}
                                      </div>
                                  ))}
                                </div>
                                <div className="flex flex-row justify-between align-center w-full">
                                  <div className="text-xs text-muted-foreground mt-2">
                                    创建于: {new Date(result.created_at + 'Z').toLocaleString(undefined, {
                                    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                                    year: 'numeric',
                                    month: '2-digit',
                                    day: '2-digit',
                                    hour: '2-digit',
                                    minute: '2-digit',
                                    second: '2-digit',
                                    hour12: false,
                                  })}
                                  </div>
                                  {result.vals.length > 3 && (
                                      <div className="cursor-pointer text-xs text-muted-foreground mt-2"
                                           onClick={() => handleEditKV(result)}>
                                        还有更多V值，点击查看
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
              </div>
            )}
          </div>
        </>
      ) : (
        /* Full-screen KV Editing Interface */
        <div className="flex flex-col h-full space-y-4 p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">编辑KV数据</h2>
          </div>

          {/* Key Input */}
          <div className="flex items-center space-x-2">
            <span className="min-w-16 text-right">Key with </span>
            <Input
              value={editKeyValue}
              onChange={(e) => setEditKeyValue(e.target.value)}
              className="flex-1"
              disabled={isLoading}
            />
          </div>

          {/* Add Button */}
          <div className="flex justify-center">
            <Button
              variant="outline"
              size="icon"
              onClick={handleAddEditValInput}
              className="rounded-full"
              disabled={isLoading}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>

          {/* Scroll Area with Val Inputs */}
          <div className="flex-1 overflow-y-auto">
            <ScrollArea className="flex-1 border rounded-md p-4">
              <div className="flex flex-col space-y-4">
                {editValInputs.map((val, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <span className="min-w-16 text-right">Val_{index} for</span>
                      <Input
                          value={val}
                          onChange={(e) => handleEditValInputChange(index, e.target.value)}
                          className="flex-1"
                          disabled={isLoading}
                      />
                    </div>
                ))}
              </div>
            </ScrollArea>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between">
            <Button onClick={handleCancelEditKV} disabled={isLoading} variant="outline">
              取消
            </Button>
            <Button onClick={handleSaveEditKV} disabled={isLoading}>
              {isLoading ? "保存中..." : "保存"}
            </Button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除这条KV数据吗？此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setKeyToDelete(null)}>取消</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteKV}>删除</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

    </div>
  );
}
