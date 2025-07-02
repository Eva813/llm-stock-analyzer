## 查詢
```
curl -X POST "http://localhost:8000/api/v1/stock/llm-report" \
     -H "Content-Type: application/json" \
     -d '{"stock_id": "SOFI"}'
{"stock_id":"SOFI","suggestion":"Wait","reason":"While the MACD is bullish and trend momentum is positive, the RSI indicates overbought conditions, suggesting a potential pullback. The CCI is also high, reinforcing the overbought signal. Although volume moving averages show increasing interest, the lack of a volume spike and the RSI's overbought status warrant caution. I'd wait for a consolidation or a pullback before considering a long position to manage risk effectively."}%  
```

## 建立一 html 介面
不需要一個像 http://... 這樣的網路網址，因為這個檔案是儲存在您自己的電腦上。


  您需要使用檔案路徑來在瀏覽器中打開它。請將以下路徑複製並貼到您的網頁瀏覽器（如
  Chrome、Safari）的網址列中，然後按下 Enter：


  file:///Users/black-star-point-frontend/llm-stock-analyzer/frontend/index.html


  或者，您可以直接在您的檔案總管 (Finder)
  中找到這個檔案，然後按兩下打開它，系統會自動用您的預設瀏覽器開啟。


  請記得：您的後端 API 服務 (uvicorn app.main:app)
  必須保持在終端機中運行，這個網頁才能成功獲取分析資料。

`python3 -m pip install uv`
`python3 -m pip install --upgrade pip `

`python3 -m venv .venv  `
 `uv sync    `
  `source .venv/bin/activate  `
  ` uvicorn app.main:app --reload`


## 專案快速運行指南
### 前置需求

Python 3.8 或更高版本
Git

1. Clone 專案
     bashgit clone <your-repository-url>
     cd <project-directory>
2. 安裝必要工具
     ```bash
     # 安裝 uv (現代 Python 套件管理工具)
     python3 -m pip install uv
     # 升級 pip (可選，但建議)
     python3 -m pip install --upgrade pip
     ```

3. 設置虛擬環境並安裝依賴
```bash
# 創建虛擬環境
python3 -m venv .venv

# 使用 uv 同步安裝所有依賴
uv sync

# 啟動虛擬環境
source .venv/bin/activate
```
4. 啟動應用程式

```bash
# 啟動開發伺服器 (支援熱重載)
uvicorn app.main:app --reload
```

停用虛擬環境

```bash
deactivate
```