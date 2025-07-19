import React, {useEffect, useState} from "react";
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle,} from "./ui/dialog";
import {Button} from "./ui/button";
import {Input} from "./ui/input";
import {Label} from "./ui/label";
import {Slider} from "./ui/slider";
import {ScrollArea} from "./ui/scroll-area";
import {Separator} from "./ui/separator";
import {Badge} from "./ui/badge";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "./ui/card";
import {Tabs, TabsContent, TabsList, TabsTrigger} from "./ui/tabs";
import {RadioGroup, RadioGroupItem} from "./ui/radio-group";
import {Download, Loader2, RefreshCw, Search, SortAsc, SortDesc, TreePine} from "lucide-react";
import {useToast} from "../hooks/use-toast";
import {
  ClusteringParams,
  ClusteringResult,
  clusterKeys,
  ClusterNode,
  exportClusteringResult,
  exportClusteringResultAsCSV,
  getClusteringStats,
  searchClusters,
  sortClustersBySimilarity,
  sortClustersBySize
} from "../services/clustering-service";

interface KViewDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function KViewDialog({ open, onOpenChange }: KViewDialogProps) {
  const [clusteringResult, setClusteringResult] = useState<ClusteringResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredClusters, setFilteredClusters] = useState<ClusterNode[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<ClusterNode | null>(null);
  const [activeTab, setActiveTab] = useState("clusters");

  // 聚类参数
  const [algorithm, setAlgorithm] = useState<'hybrid' | 'similarity' | 'pattern'>('hybrid');
  const [similarityThreshold, setSimilarityThreshold] = useState([0.6]);
  const [minClusterSize, setMinClusterSize] = useState([2]);

  // 排序和过滤
  const [sortBy, setSortBy] = useState<'size' | 'similarity'>('size');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showSingletons, setShowSingletons] = useState(true);

  const { toast } = useToast();

  // 执行聚类
  const performClustering = async () => {
    setLoading(true);
    try {
      const params: ClusteringParams = {
        algorithm,
        similarity_threshold: similarityThreshold[0],
        min_cluster_size: minClusterSize[0]
      };

      const result = await clusterKeys(params);
      setClusteringResult(result);
      setFilteredClusters(result.clusters);
      setSelectedCluster(null);

      toast({
        title: "聚类完成",
        description: `发现 ${result.total_clusters} 个聚类，包含 ${result.total_keys} 个键`,
      });
    } catch (error) {
      console.error("Clustering failed:", error);
      toast({
        title: "聚类失败",
        description: error instanceof Error ? error.message : "未知错误",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // 搜索和过滤
  useEffect(() => {
    if (!clusteringResult) return;

    let clusters = clusteringResult.clusters;

    // 搜索过滤
    if (searchQuery.trim()) {
      clusters = searchClusters(clusters, searchQuery);
    }

    // 单例过滤
    if (!showSingletons) {
      clusters = clusters.filter(cluster => cluster.size > 1);
    }

    // 排序
    if (sortBy === 'size') {
      clusters = sortClustersBySize(clusters, sortOrder === 'asc');
    } else {
      clusters = sortClustersBySimilarity(clusters, sortOrder === 'asc');
    }

    setFilteredClusters(clusters);
  }, [clusteringResult, searchQuery, showSingletons, sortBy, sortOrder]);

  // 导出功能
  const handleExport = (format: 'json' | 'csv') => {
    if (!clusteringResult) return;

    try {
      let content: string;
      let filename: string;
      let mimeType: string;

      if (format === 'json') {
        content = exportClusteringResult(clusteringResult);
        filename = `k-view-clusters-${Date.now()}.json`;
        mimeType = 'application/json';
      } else {
        content = exportClusteringResultAsCSV(clusteringResult);
        filename = `k-view-clusters-${Date.now()}.csv`;
        mimeType = 'text/csv';
      }

      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast({
        title: "导出成功",
        description: `聚类结果已导出为 ${format.toUpperCase()} 格式`,
      });
    } catch (error) {
      toast({
        title: "导出失败",
        description: "无法导出聚类结果",
        variant: "destructive",
      });
    }
  };

  // 获取统计信息
  const stats = clusteringResult ? getClusteringStats(clusteringResult) : null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-screen h-screen max-w-none max-h-none overflow-hidden">
        <DialogHeader className="flex min-h-0">
          <DialogTitle className="flex items-center gap-2">
            <TreePine className="h-5 w-5" />
            K视图探索
          </DialogTitle>
          <DialogDescription>
            通过智能聚类算法探索和分析键值对中的K值模式
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 flex-col h-full overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col h-full overflow-hidden">
            <TabsList className="grid w-full grid-cols-3 flex-shrink-0">
              <TabsTrigger value="clusters">聚类结果</TabsTrigger>
              <TabsTrigger value="settings">聚类设置</TabsTrigger>
              <TabsTrigger value="stats">统计信息</TabsTrigger>
            </TabsList>

            {/* 聚类结果标签页 */}
            <TabsContent value="clusters">
              {/* 工具栏 */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 flex-shrink-0">
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 flex-1 w-full sm:w-auto">
                  <div className="relative w-full sm:flex-1 sm:max-w-sm">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="搜索聚类..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-8"
                    />
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSortBy(sortBy === 'size' ? 'similarity' : 'size')}
                    >
                      {sortBy === 'size' ? '按大小' : '按相似度'}
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                    >
                      {sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-wrap w-full sm:w-auto">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowSingletons(!showSingletons)}
                  >
                    {showSingletons ? '隐藏单例' : '显示单例'}
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExport('json')}
                    disabled={!clusteringResult}
                  >
                    <Download className="h-4 w-4 mr-1" />
                    JSON
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExport('csv')}
                    disabled={!clusteringResult}
                  >
                    <Download className="h-4 w-4 mr-1" />
                    CSV
                  </Button>
                </div>
              </div>

              <div className="flex-1">
                {/* 聚类结果显示 */}
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 mt-4 min-h-0" style={{ height: 'calc(100vh - 240px)' }}>
                  {/* 聚类列表 */}
                  <Card className="flex flex-col sm:mt-1 lg:mx-1 min-h-0">
                    <CardHeader className="flex-shrink-0 pb-3">
                      <CardTitle className="text-sm">
                        聚类列表 ({filteredClusters.length})
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0 flex-1 min-h-0 overflow-y-auto">
                      <ScrollArea className="h-full">
                        <div className="space-y-2 p-4 pb-2">
                          {filteredClusters.map((cluster) => (
                              <Card
                                  key={cluster.id}
                                  className={`cursor-pointer transition-colors ${
                                      selectedCluster?.id === cluster.id
                                          ? 'bg-primary/10 border-primary'
                                          : 'hover:bg-secondary/50'
                                  }`}
                                  onClick={() => setSelectedCluster(cluster)}
                              >
                                <CardContent className="p-3">
                                  <div className="flex items-center justify-between mb-2">
                                    <Badge variant="outline">
                                      {cluster.size} 个键
                                    </Badge>
                                    {cluster.similarity_score > 0 && (
                                        <Badge variant="secondary">
                                          相似度: {(cluster.similarity_score * 100).toFixed(1)}%
                                        </Badge>
                                    )}
                                  </div>

                                  {cluster.pattern && (
                                      <div className="text-xs text-muted-foreground mb-2">
                                        模式: {cluster.pattern}
                                      </div>
                                  )}

                                  <div className="text-sm">
                                    {cluster.keys.slice(0, 3).map((key, index) => (
                                        <div key={index} className="truncate">
                                          {key}
                                        </div>
                                    ))}
                                    {cluster.keys.length > 3 && (
                                        <div className="text-muted-foreground">
                                          ... 还有 {cluster.keys.length - 3} 个
                                        </div>
                                    )}
                                  </div>
                                </CardContent>
                              </Card>
                          ))}

                          {filteredClusters.length === 0 && !loading && (
                              <div className="text-center text-muted-foreground py-8">
                                {clusteringResult ? '没有找到匹配的聚类' : '点击"开始聚类"按钮开始分析'}
                              </div>
                          )}
                        </div>
                      </ScrollArea>
                    </CardContent>
                  </Card>

                  {/* 聚类详情 */}
                  <Card className="flex flex-1 flex-col min-h-0 sm:mt-1 lg:mx-1">
                    <CardHeader className="flex-shrink-0 pb-3">
                      <CardTitle className="text-sm">聚类详情</CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1 min-h-0 p-4 h-full overflow-y-auto">
                      {selectedCluster ? (
                          <ScrollArea className="h-full">
                            <div className="space-y-1">
                              {selectedCluster.keys.map((key, index) => (
                                  <div
                                      key={index}
                                      className="text-sm font-mono bg-secondary/30 px-2 py-1 rounded break-all"
                                  >
                                    {key}
                                  </div>
                              ))}
                            </div>
                          </ScrollArea>
                      ) : (
                          <div className="text-center text-muted-foreground py-8">
                            选择一个聚类查看详情
                          </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>

            {/* 聚类设置标签页 */}
            <TabsContent value="settings">
              <div className="flex-1" style={{ height: 'calc(100vh - 190px)' }}>
                <Card>
                  <CardHeader>
                    <CardTitle>聚类算法</CardTitle>
                    <CardDescription>
                      选择适合您数据特征的聚类算法
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <RadioGroup value={algorithm} onValueChange={(value) => setAlgorithm(value as any)}>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="hybrid" id="hybrid" />
                        <Label htmlFor="hybrid" className="flex-1">
                          <div className="font-medium">混合聚类（推荐）</div>
                          <div className="text-sm text-muted-foreground">
                            结合模式识别和相似度计算的智能聚类
                          </div>
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="similarity" id="similarity" />
                        <Label htmlFor="similarity" className="flex-1">
                          <div className="font-medium">相似度聚类</div>
                          <div className="text-sm text-muted-foreground">
                            基于字符串相似度的层次聚类
                          </div>
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="pattern" id="pattern" />
                        <Label htmlFor="pattern" className="flex-1">
                          <div className="font-medium">模式聚类</div>
                          <div className="text-sm text-muted-foreground">
                            基于正则表达式模式的分组聚类
                          </div>
                        </Label>
                      </div>
                    </RadioGroup>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>聚类参数</CardTitle>
                    <CardDescription>
                      调整参数以获得最佳聚类效果
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div>
                      <Label>相似度阈值: {similarityThreshold[0].toFixed(2)}</Label>
                      <Slider
                          value={similarityThreshold}
                          onValueChange={setSimilarityThreshold}
                          max={1}
                          min={0}
                          step={0.05}
                          className="mt-2"
                      />
                      <div className="text-sm text-muted-foreground mt-1">
                        较高的阈值产生更严格的聚类
                      </div>
                    </div>

                    <div>
                      <Label>最小聚类大小: {minClusterSize[0]}</Label>
                      <Slider
                          value={minClusterSize}
                          onValueChange={setMinClusterSize}
                          max={10}
                          min={1}
                          step={1}
                          className="mt-2"
                      />
                      <div className="text-sm text-muted-foreground mt-1">
                        聚类中包含的最少键数量
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <div className="flex justify-center mt-4">
                  <Button
                      onClick={performClustering}
                      disabled={loading}
                      size="lg"
                      className="min-w-[200px]"
                  >
                    {loading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          聚类中...
                        </>
                    ) : (
                        <>
                          <RefreshCw className="mr-2 h-4 w-4" />
                          开始聚类
                        </>
                    )}
                  </Button>
                </div>
              </div>
            </TabsContent>

            {/* 统计信息标签页 */}
            <TabsContent value="stats">
              <div className="flex-1" style={{ height: 'calc(100vh - 190px)' }}>
                <ScrollArea className="flex-1 h-full">
                  <div className="p-4 pb-6">
                    {stats ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                          <Card>
                            <CardHeader className="pb-2">
                              <CardTitle className="text-sm">基本统计</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2">
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">总键数</span>
                                <span className="font-medium">{stats.totalKeys}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">聚类数</span>
                                <span className="font-medium">{stats.totalClusters}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">平均聚类大小</span>
                                <span className="font-medium">{stats.averageClusterSize.toFixed(1)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">单例聚类</span>
                                <span className="font-medium">{stats.singletonClusters}</span>
                              </div>
                            </CardContent>
                          </Card>

                          <Card>
                            <CardHeader className="pb-2">
                              <CardTitle className="text-sm">聚类大小</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2">
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">最大聚类</span>
                                <span className="font-medium">{stats.largestCluster}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">最小聚类</span>
                                <span className="font-medium">{stats.smallestCluster}</span>
                              </div>
                            </CardContent>
                          </Card>

                          <Card>
                            <CardHeader className="pb-2">
                              <CardTitle className="text-sm">算法信息</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2">
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">算法</span>
                                <span className="font-medium break-all">{stats.algorithm}</span>
                              </div>
                              {stats.parameters.similarity_threshold && (
                                  <div className="flex justify-between">
                                    <span className="text-sm text-muted-foreground">相似度阈值</span>
                                    <span className="font-medium">{stats.parameters.similarity_threshold}</span>
                                  </div>
                              )}
                              {stats.parameters.min_cluster_size && (
                                  <div className="flex justify-between">
                                    <span className="text-sm text-muted-foreground">最小聚类大小</span>
                                    <span className="font-medium">{stats.parameters.min_cluster_size}</span>
                                  </div>
                              )}
                            </CardContent>
                          </Card>

                          <Card className="sm:col-span-2 xl:col-span-3">
                            <CardHeader className="pb-2">
                              <CardTitle className="text-sm">模式分布</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-2">
                                {Object.entries(stats.patternDistribution).map(([pattern, count]) => (
                                    <div key={pattern} className="flex items-center justify-between bg-secondary/30 px-3 py-2 rounded">
                                      <span className="text-sm break-all">{pattern}</span>
                                      <Badge variant="secondary">{count}</Badge>
                                    </div>
                                ))}
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                    ) : (
                        <div className="text-center text-muted-foreground py-8">
                          执行聚类后查看统计信息
                        </div>
                    )}
                  </div>
                </ScrollArea>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
}