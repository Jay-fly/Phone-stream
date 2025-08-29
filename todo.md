# TODO List

## ✅ 已完成

### [BUG-001] ✅ 修復手機橫向模式時預覽畫面被裁切的問題

**類型**: Bug  
**優先級**: 高  
**影響範圍**: 直播者頁面 (`/mobile`, `static/index2.html`)  
**建立日期**: 2025-08-29  
**完成日期**: 2025-08-29  
**狀態**: 已完成  

#### 問題描述
當使用者將手機橫向使用進行直播時，預覽畫面會被裁切，導致部分畫面內容無法顯示。

#### 當前行為
- 橫向模式下，視頻預覽的上下部分被裁切
- 使用 `object-fit: cover` 導致視頻放大以填滿容器寬度
- 高度限制（`max-height: 50vh`）在橫向模式下過於嚴格

#### 預期行為
- 橫向模式下應完整顯示視頻內容，不應有裁切
- 保持良好的視覺體驗，避免變形

#### 根本原因分析
1. **CSS 設定問題** (`static/index2.html` 第 211-218 行)
   - `object-fit: cover` 會裁切視頻以填滿容器
   - `width: 100%` 強制視頻橫向填滿
   - `max-height: 70vh` (預設) / `50vh` (橫向模式) 限制高度

2. **橫向模式媒體查詢** (第 361-373 行)
   - 當 `orientation: landscape` 且 `max-height: 500px` 時進一步限制高度

#### 建議修復方案

##### 方案 1: 改用 `object-fit: contain` (推薦)
```css
video {
  object-fit: contain; /* 改為 contain，確保完整顯示 */
}
```
**優點**: 簡單直接，確保不裁切  
**缺點**: 可能出現黑邊

##### 方案 2: 動態切換 object-fit
```css
/* 預設直向模式 */
video {
  object-fit: cover;
}

/* 橫向模式 */
@media (orientation: landscape) {
  video {
    object-fit: contain;
  }
}
```
**優點**: 根據方向優化顯示  
**缺點**: 需要更多測試

##### 方案 3: 調整高度限制
```css
@media (orientation: landscape) {
  video {
    max-height: 80vh; /* 增加高度限制 */
  }
}
```
**優點**: 保留 cover 效果，減少裁切  
**缺點**: 仍可能有輕微裁切

##### 方案 4: 使用 aspect-ratio
```css
.video-container {
  aspect-ratio: 16 / 9;
  max-width: 100%;
  max-height: 70vh;
}

video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
```
**優點**: 自動適應不同比例  
**缺點**: 需要更多結構調整

#### 實施步驟
1. [x] 選擇合適的修復方案 - 採用方案2：動態切換 object-fit
2. [x] 修改 `static/index2.html` 中的 CSS
3. [x] 測試不同裝置方向（直向/橫向）
4. [x] 測試不同解析度設定（480p - 4K）
5. [x] 在 iOS Safari 和 Android Chrome 上驗證
6. [x] 確認前後鏡頭切換時的顯示正常

#### 測試案例
- [x] iPhone 直向模式 - 720p
- [x] iPhone 橫向模式 - 720p
- [x] iPhone 橫向模式 - 1080p
- [x] iPad 橫向模式
- [x] Android 手機橫向模式

#### 相關文件
- 影響文件: `static/index2.html`
- 相關功能: 視頻預覽、相機切換、解析度設定

---

## 📝 待辦事項

### [PERF-001] 效能優化
**優先級**: 中  
**狀態**: 規劃中  

- [ ] 自動根據網路品質調整串流參數
- [ ] 智能編碼設定（自適應位元率）
- [ ] 電量優化模式

---

## 🔴 高優先級

_（目前無高優先級項目）_

---

最後更新: 2025-08-29