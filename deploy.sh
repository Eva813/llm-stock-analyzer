#!/bin/bash

# Cloud Run 部署腳本
# 請確保已經登入 gcloud 並設定正確的專案

set -e

# 設定變數
PROJECT_ID="coral-balancer-464807-h8"
SERVICE_NAME="llm-stock-analyzer"
REGION="asia-east1"  # 台灣地區
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 開始部署 LLM Stock Analyzer 到 Cloud Run..."

# 確認 gcloud 配置
echo "📋 檢查 gcloud 配置..."
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# 啟用必要的 API
echo "🔧 啟用 Cloud Run 和 Container Registry API..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 建構並推送 Docker 映像檔
echo "🏗️ 建構 Docker 映像檔..."
docker build -t $IMAGE_NAME:latest .

echo "📤 推送映像檔到 Container Registry..."
docker push $IMAGE_NAME:latest

# 部署到 Cloud Run
echo "🚀 部署到 Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300s \
  --max-instances 10 \
  --min-instances 0 \
  --concurrency 80 \
  --set-env-vars "PORT=8080,PYTHONUNBUFFERED=1"

# 取得服務 URL
echo "✅ 部署完成！"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo "🌐 服務 URL: $SERVICE_URL"
echo "🔍 健康檢查: $SERVICE_URL/health"
echo "📚 API 文件: $SERVICE_URL/docs"

# 測試健康檢查
echo "🏥 測試健康檢查..."
curl -f $SERVICE_URL/health || echo "⚠️ 健康檢查失敗，請檢查服務狀態"

echo "🎉 部署完成！前端工程師可以使用以下 endpoint:"
echo "Base URL: $SERVICE_URL"
echo "API Version: $SERVICE_URL/api/v1"
