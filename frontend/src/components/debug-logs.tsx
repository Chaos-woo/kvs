import React from 'react';
import { Button } from './ui/button';
import { logger } from '../utils/logger';
import { toast } from './ui/use-toast';

export function DebugLogs() {

  const handleGetLogPath = async () => {
    try {
      const logPath = await logger.getLogDirectoryPath();
      if (logPath) {
        toast({
          title: '日志目录路径',
          description: logPath,
        });
      } else {
        toast({
          title: '获取日志路径失败',
          description: '日志路径不可用。请检查应用权限并确保日志目录已正确创建。如果问题持续存在，请尝试以管理员身份运行应用程序。',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error getting log path:', error);
      toast({
        title: '获取日志路径失败',
        description: `错误: ${error}。请检查应用权限并尝试以管理员身份运行应用程序。`,
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="flex flex-col space-y-2 p-4 border rounded-md">
      <h3 className="text-lg font-medium">调试日志</h3>
      <p className="text-sm text-muted-foreground">
        访问应用日志文件以帮助调试问题
      </p>
      <div className="flex flex-row space-x-2 mt-2">
        <Button variant="outline" size="sm" onClick={handleGetLogPath}>
          显示日志路径
        </Button>
      </div>
    </div>
  );
}

export default DebugLogs;
