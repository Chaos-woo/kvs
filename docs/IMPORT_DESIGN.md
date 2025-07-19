# KV数据导入功能设计

## 功能需求分析
- 导入JSONL格式文件，单行格式：{"k":"str","v":["str"],"create_at":"timestamp"}
- 支持全量导入和选择性导入
- 全屏模态对话框，参考cleanup-dialog.tsx的UI设计
- 文件选择器仅支持.jsonl后缀
- 数据格式强校验（k、v、create_at字段存在性和类型）
- 显示无效数据数量（红字提示）
- 导入完成后toast提示

## UI组件设计

### 1. 菜单项添加
- 在menu-bar.tsx的"应用"菜单中添加"数据导入"选项
- 位置：在"数据导出"之前

### 2. ImportDialog组件
基于cleanup-dialog.tsx的设计模式：
- 使用AlertDialog全屏覆盖
- 分为三个阶段：
  1. 文件选择阶段
  2. 数据预览和选择阶段  
  3. 导入进度阶段

#### 组件结构：
```typescript
interface ImportData {
  k: string;
  v: string[];
  create_at: string;
  valid: boolean;
  error?: string;
}

interface ImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onImportComplete?: () => void;
}
```

#### UI阶段设计：
1. **文件选择阶段**：
   - 文件选择按钮（仅.jsonl）
   - 文件信息显示
   - "下一步"按钮

2. **数据预览阶段**：
   - 类似cleanup-dialog的数据列表
   - 全选/取消全选功能
   - 显示有效/无效数据统计
   - 无效数据红字提示
   - "取消"和"导入"按钮

3. **导入进度阶段**：
   - 进度条显示
   - 导入状态信息

## 后端API设计

### 新增端点：POST /api/v1/kv/import

#### 请求格式：
```json
{
  "data": [
    {
      "k": "key1",
      "v": ["value1", "value2"],
      "create_at": "2025-07-19T08:04:00Z"
    }
  ]
}
```

#### 响应格式：
```json
{
  "status": "success",
  "data": {
    "imported_count": 10,
    "failed_count": 2,
    "total_count": 12,
    "failed_items": [
      {
        "index": 5,
        "error": "Invalid data format"
      }
    ]
  }
}
```

## 数据验证逻辑

### 前端验证：
1. 文件格式验证（.jsonl后缀）
2. JSONL解析验证
3. 每行数据结构验证：
   - k字段存在且为字符串
   - v字段存在且为字符串数组
   - create_at字段存在且为有效时间戳

### 后端验证：
1. 请求数据格式验证
2. 重复数据检查（可选）
3. 数据库约束验证

## 实现步骤

### 前端实现：
1. 修改menu-bar.tsx添加"数据导入"菜单项
2. 创建ImportDialog组件
3. 实现文件选择和解析逻辑
4. 实现数据预览和选择界面
5. 实现导入API调用和进度显示

### 后端实现：
1. 在routes/kv.py添加import_kv_data端点
2. 实现JSONL数据解析和验证
3. 批量创建KV数据的逻辑
4. 错误处理和响应格式化

### 集成测试：
1. 创建测试JSONL文件
2. 测试各种边界情况
3. 测试错误处理流程