# OKBet Weekly Bonus Card — 前台互動規格書

> Prototype 參考：`weekly-card-h5-v1.html`
> 最後更新：2026-05-22

---

## 目錄

1. [全域規則](#1-全域規則)
2. [購買頁](#2-購買頁)
3. [領取頁](#3-領取頁)
4. [登錄自動派發](#4-登錄自動派發)
5. [提示彈窗](#5-提示彈窗)
6. [存款頁面彈窗](#6-存款頁面彈窗)
7. [確認離開彈窗](#7-確認離開彈窗)
8. [Modals](#8-modals)
9. [獎勵資料表](#9-獎勵資料表)
10. [後端欄位對應](#10-後端欄位對應)

---

## 1. 全域規則

| # | 規則 | 說明 |
|---|------|------|
| G1 | 每周限購一張 | 玩家同時只能持有一張（Classic 或 Premium），7 天週期完全結束後才可重購 |
| G2 | 兩種卡互斥 | 持有任一卡時，另一卡的購買按鈕顯示為 disabled（灰色） |
| G3 | 每日重置時間 | 每天 **11:59:59 PM** 重置所有當日簽到狀態、任務進度與未領取獎勵 |
| G4 | 過期即作廢 | 當日未登入 / 未完成任務 / 未手動領取 → 獎勵永久作廢，不補發 |
| G5 | Turnover 要求 | 所有獎勵附流水要求，倍率 TBD，發放時自動套用 |
| G6 | CLAIM_MODE | 後台可設定 `auto`（登入自動派發）或 `manual`（需手動領取）；影響日常簽到的發放方式與 T&C 第2條文字 |

---

## 2. 購買頁

### 2.1 組件狀態表

| 組件 | 狀態 | 外觀 / 行為 |
|------|------|-------------|
| Plan Tab — Classic | 選中 | 粉色邊框、背景粉色透明、右下角顯示 ✓ |
| Plan Tab — Classic | 未選中 | 預設半透明背景 |
| Plan Tab — Classic | 已購買 | 左下角顯示「✓ 已購」綠色 tag |
| Plan Tab — Premium | 選中 | 紫色邊框、背景紫色透明、顯示「推荐」badge |
| Buy Now 按鈕 | 預設 | 漸層粉色，可點擊 |
| Buy Now 按鈕 | Premium 選中 | 漸層紫色 |
| Buy Now 按鈕 | 已購買同款 | 文字改為「每周限購一次」，綠色樣式，不可點擊 |
| Buy Now 按鈕 | 已購買他款 | 文字改為「每周限購一次」，灰色樣式，不可點擊 |
| Weekly Rewards 表格 | — | 橫向捲動，第一欄 sticky，依選中方案切換資料 |
| 規則按鈕（右側 Tab）| — | 固定在 Hero 右側，點擊開啟 Rules Modal |

### 2.2 互動觸發表

| 觸發 | 條件 | 執行動作 |
|------|------|----------|
| 點擊 Plan Tab | — | 切換選中方案，更新 Detail Card、Weekly Rewards 表格 |
| 點擊 Buy Now | `purchasedPlan === null` | 開啟 Buy Confirm Modal |
| 點擊 Buy Now | `purchasedPlan !== null` | 無反應（按鈕已 disabled） |
| 點擊「規則」Tab | — | 開啟 Rules Modal |

---

## 3. 領取頁

### 3.1 組件狀態表

| 組件 | 狀態 | 外觀 / 行為 |
|------|------|-------------|
| 進度條 | — | `已完成天數 / 7` 換算為百分比寬度 |
| Day Row — done | 已完成 | 日期圈綠色 ✓，基本獎勵顯示 chip + ✓，額外獎勵依領取狀態顯示 |
| Day Row — today | 今日 | 展開卡片樣式，粉色邊框，顯示「今日」tag |
| Day Row — locked | 未解鎖 | 整列半透明，顯示「未解锁」文字 |
| Day Row — prize | 第7天 | 金色特殊樣式 |

### 3.2 日常簽到（Basic）欄位狀態

| 狀態 | 按鈕 / 顯示 |
|------|-------------|
| done | 綠色 ✓ check circle |
| today（Classic Card） | **Claim** 按鈕（粉色）→ 點擊後彈出 Claim Popup，完成後顯示綠色 ✓ |
| today（Premium Card） | 綠色 ✓ check circle（auto-dispatched） |
| locked | 「未解锁」灰色文字 |

### 3.3 每日任務（Extra）欄位狀態

| 狀態 | 條件 | 按鈕 |
|------|------|------|
| done + 已領取 | `extraClaimed` 含此 key | `✓ Claimed`（綠色，不可點） |
| done + 未領取 | 超過當日 | `Expired`（紅色，不可點） |
| today + condMet = true | 條件已達成 | `领取`（粉色）→ 點擊開啟 Claim Popup |
| today + condMet = false + 條件為「投注」 | — | `Deposit`（粉色）→ 導至存款頁 |
| today + condMet = false + 條件為「存款」 | — | `Play Now`（金色）→ 導至遊戲頁 |
| locked | — | 僅顯示條件文字，無按鈕 |

### 3.4 互動觸發表

| 觸發 | 條件 | 執行動作 |
|------|------|----------|
| 點擊 Claim（日常簽到） | Classic Card today | 標記為已領取，開啟 Claim Popup，重繪列表 |
| 點擊「领取」（每日任務） | condMet = true | 標記 extraClaimed，開啟 Claim Popup，重繪列表 |
| 點擊「Deposit」 | 條件含「投注」 | 導至存款頁面 |
| 點擊「Play Now」 | 條件含「存款」 | 導至遊戲頁面 |
| 點擊「規則」Tab | — | 開啟 Rules Modal |

---

## 4. 登錄自動派發

> 觸發時機：`CLAIM_MODE = 'auto'`，玩家登入後系統自動派發當日日常簽到獎勵

### 4.1 組件說明

| 組件 | 說明 |
|------|------|
| Auto tag | 顯示「⚡ Automatically Claimed Upon Login」 |
| 標題 | 顯示「Day X Daily Reward Successfully Claimed」，X 為當日天數 |
| 進度圓點 | 7 個，顯示 done / today / locked 三種狀態 |
| 獎勵列表 | 顯示已自動派發的日常簽到獎勵，標示「✓ Credited」 |
| 額外獎勵區塊 | 顯示當日 extra 獎勵與完成條件，提供快捷按鈕 |
| Confirm 按鈕 | 點擊關閉此 Bottom Sheet |

### 4.2 互動觸發表

| 觸發 | 執行動作 |
|------|----------|
| 玩家登入 + CLAIM_MODE = auto | 自動派發日常獎勵，顯示此 Bottom Sheet |
| 點擊 Confirm | 關閉 Bottom Sheet |
| 點擊 Play Now（extra 區塊）| 導至對應遊戲 / 存款頁面 |

---

## 5. 提示彈窗

> 以 Banner 形式出現，不阻斷操作流程

### 5.1 兩種類型

| 類型 | 觸發時機 | 內容 |
|------|----------|------|
| 任務完成 | 玩家完成當日任務條件 | 「Weekly Card Task Completed！」+ 可領取的 extra 獎勵 |
| 日常簽到 | CLAIM_MODE = manual，玩家當日尚未領取日常獎勵 | 「Weekly Card Daily Reward Available！」+ 獎勵金額 |

### 5.2 互動觸發表

| 觸發 | 執行動作 |
|------|----------|
| 點擊 ✕ | 該 Banner 淡出消失（不再顯示，當日有效） |

---

## 6. 存款頁面彈窗

> 玩家進入存款頁面時，若尚未購買週卡，自動顯示此彈窗

### 6.1 組件說明

| 組件 | 說明 |
|------|------|
| Banner | 顯示活動名稱、副標、活動期間 |
| Premium Card 欄 | 顯示方案名稱、價格、7天總獎勵 chips |
| Classic Card 欄 | 同上 |
| View Now 按鈕 | 導至週卡購買頁 |
| Don't Show Again Today | 勾選後當日不再顯示此彈窗 |
| ✕ 關閉按鈕 | 關閉彈窗，回到存款頁面 |

### 6.2 顯示條件

| 條件 | 是否顯示 |
|------|----------|
| 玩家未購買週卡 | ✅ 顯示 |
| 玩家已購買週卡 | ❌ 不顯示 |
| 玩家當日已勾選「Don't Show Again Today」 | ❌ 不顯示 |

### 6.3 互動觸發表

| 觸發 | 執行動作 |
|------|----------|
| 點擊 View Now | 導至購買頁 |
| 點擊 ✕ | 關閉彈窗 |
| 勾選 Don't Show Again Today | 當日 session 記錄，不再顯示 |

---

## 7. 確認離開彈窗

> 玩家在存款頁面彈窗顯示期間，點擊返回或其他離開操作時觸發

### 7.1 互動觸發表

| 觸發 | 執行動作 |
|------|----------|
| 點擊「Go to Purchase」 | 關閉確認彈窗，導至購買頁 |
| 點擊「Leave」 | 關閉所有彈窗，離開當前頁面 |

---

## 8. Modals

### 8.1 Buy Confirm Modal

> 點擊「Buy Now」後觸發

| 組件 | 說明 |
|------|------|
| 方案名稱 | 動態顯示選中的方案 |
| 價格 | 動態顯示 |
| 購買須知 | 4 條固定說明（即時生效、每日自動、完成任務、不可退款） |
| Confirm Purchase | 確認購買，記錄 `purchasedPlan`，顯示 Toast「購買成功」 |
| Cancel | 關閉 Modal |
| 點擊背景 | 關閉 Modal |

### 8.2 Rules Modal（T&C）

> 點擊任何「規則」Tab 觸發

| 行為 | 說明 |
|------|------|
| 開啟 | body `overflow:hidden`，Modal 縮放動畫進場 |
| 關閉 | 點擊 ✕ 或點擊背景 |

### 8.3 Claim Popup（Bottom Sheet）

> 點擊「Claim」或「领取」後觸發

| 組件 | 說明 |
|------|------|
| 標題 | 動態顯示「第 X 天 日常簽到 / 額外獎勵」 |
| 獎勵卡片 | 顯示 icon + 金額/數量 + 類型名稱 |
| 關閉 | 點擊 ✕ 或點擊背景遮罩 |

---

## 9. 獎勵資料表

### Classic Card（500 PHP / 7天）

| 天 | 日常簽到 | 每日任務條件 | 每日任務獎勵 |
|----|----------|--------------|--------------|
| 1 | 💵 50 PHP | 存款 ≥ 200 PHP | ⭐ 80 pts |
| 2 | ⭐ 100 pts | 存款 ≥ 200 PHP | 🎰 ×5 |
| 3 | 🎰 ×8 | 存款 ≥ 300 PHP | 💵 30 PHP |
| 4 | 💵 70 PHP | 投注 ≥ 500 PHP | 🎟 Acewin Free Spins ×1 |
| 5 | 🎟 ×1 | 存款 ≥ 400 PHP | 💵 60 PHP |
| 6 | ⭐ 150 pts | 投注 ≥ 400 PHP | 🎟 Acewin Free Spins ×1 |
| 7 | 💵 120 PHP | 存款 ≥ 500 PHP | 🎰 ×15 |

### Premium Card（2,000 PHP / 7天）

| 天 | 日常簽到 | 每日任務條件 | 每日任務獎勵 |
|----|----------|--------------|--------------|
| 1 | 💵 200 PHP | 存款 ≥ 500 PHP | ⭐ 300 pts |
| 2 | ⭐ 500 pts | 存款 ≥ 500 PHP | 🎰 ×15 |
| 3 | 🎰 ×20 | 存款 ≥ 800 PHP | 💵 100 PHP |
| 4 | 💵 250 PHP | 存款 ≥ 1,000 PHP | 🎟 Acewin Free Spins ×2 |
| 5 | 🎟 ×2 | 存款 ≥ 1,000 PHP | 💵 150 PHP |
| 6 | ⭐ 800 pts | 存款 ≥ 1,500 PHP | 🎟 Acewin Free Spins ×1 |
| 7 | 💵 500 PHP | 存款 ≥ 2,000 PHP | 🎰 ×30 |

---

## 10. 後端欄位對應

### 10.1 玩家週卡狀態（API Response）

| 欄位 | 型別 | 說明 |
|------|------|------|
| `has_card` | Boolean | 是否持有週卡 |
| `card_type` | String | `"classic"` \| `"premium"` \| `null` |
| `card_expire_at` | Timestamp | 週卡到期時間 |
| `current_day` | Integer | 當前第幾天（1–7） |
| `claim_mode` | String | `"auto"` \| `"manual"` |
| `days` | Array | 每天的狀態陣列，見下表 |

### 10.2 每日狀態物件（`days[]`）

| 欄位 | 型別 | 說明 |
|------|------|------|
| `day` | Integer | 第幾天（1–7） |
| `status` | String | `"done"` \| `"today"` \| `"locked"` |
| `basic_claimed` | Boolean | 日常簽到是否已領取 |
| `extra_condition_met` | Boolean | 每日任務條件是否達成 |
| `extra_claimed` | Boolean | 每日任務獎勵是否已領取 |
| `extra_expired` | Boolean | 每日任務獎勵是否已過期 |

### 10.3 存款頁彈窗控制

| 欄位 | 型別 | 說明 |
|------|------|------|
| `show_deposit_popup` | Boolean | 是否顯示存款頁彈窗（後端判斷未購卡 + 未勾選不再顯示） |
| `deposit_popup_dismissed_today` | Boolean | 玩家當日是否已勾選「Don't Show Again Today」|
