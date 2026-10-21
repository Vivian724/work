# 獎勵中心（/reward-center、/m/reward-center）API 與後端活動設定對照

> 調查日期：2026-10-19
> 前端：ok-web；後端：cx-okbet-parent、module-*，分支 master（與 origin/master 一致）
> 只讀調查，未改任何程式。行號以調查當下的 master 為準。
> 標 `not verified` 的項目沒有在程式碼中逐行確認。

路徑縮寫：
- `UIC` = `cx-okbet-parent/cx-sport-app-service/.../cp/controller/front/UserIndexController.java`
- `IMS` = `module-basic/basic-service/.../cp/service/setting/ImageManageServiceImpl.java`
- `AAS` = `module-activity/activity-service/.../sports/service/activity/AgentActivityServiceImpl.java`

---

## 一、前端 API 總表

| # | API | 端 | 登入 | 什麼時候打（前端） | 前端位置 |
|---|---|---|---|---|---|
| 1 | `GET /api/front/index/activityCategoryList` | H5 + PC | 不需 | 進頁、切語系 | `pages/Activities/index.tsx` |
| 2 | `GET /api/front/index/activityImageListH5?activityCategoryId=` | H5 | 不需 | 進頁、**點標籤**、切語系、角標數變化 | 同上 |
| 3 | `GET /api/front/index/activityImageListPc?activityCategoryId=` | PC | 不需 | 同上 | 同上 |
| 4 | `GET /api/front/index/activityImagePendingClaimCountH5` / `...Pc` | 全站 | **需要** | 換頁、切語系、領獎後、**每 2 分鐘輪詢** | `store/activity/usePendingClaimBadge.ts`、`layout/MobileLayout`、`layout/WebLayout` |
| 5 | `POST /api/front/rewardCenterActivity/rewardCenterActivityList` | PC | 不需 | 進頁、切語系 | `pages/RewardCenter/NewActivity.tsx` |
| 6 | `GET /api/front/promotions` | PC | 不需 | 進頁 | `pages/RewardCenter/hooks/useWelfare.ts` |
| 7 | `GET /api/front/activity/normalSignStatus` | PC | 不需 | 進頁 | `pages/RewardCenter/hooks/useSignIn.ts` |
| 8 | `GET /api/front/activity/bonus-calendar/month`、`/recent` | PC | 需要 | 進頁 | `useSignIn.ts`、`useWelfare.ts` |
| 9 | `GET /api/front/dailySpecialActivity/userInfo` | 全站 | 需要 | 換頁 | `store/activity/useDailySpecial.ts` |
| 10 | `GET /api/front/quest/info`、`/quest/guest/info` | H5 + PC | 依登入二選一 | 進頁 | `TaskCenter`（H5）、`hooks/useQuestInfo.ts`（PC） |
| 11 | `GET /api/front/freeSpin/queryListFront` | PC | 不需 | 進頁 | `hooks/useFreeSgin.ts` |
| 12 | `GET /api/front/freeSpin/queryCouponTotalCount` | H5 + PC | 需要 | 進頁 | `components/UserDetail` |
| 13 | `GET /api/front/coupon-system/queryAll` | H5 + PC | 需要 | 進頁 | `pages/RewardCenter/hooks/useDetail.ts` |
| 14 | `GET /api/front/product/index`、`/product/guest/index` | H5 + PC | 依登入二選一 | 進頁、切語系 | `hooks/usePointMalls.ts` |
| 15 | `GET /api/front/activity/vip/user`、`/vip/detail` | PC | 需要 | 進頁 | `hooks/useUserVipInfo.ts` |

H5 點分類標籤只會重打 #2（帶新的 `activityCategoryId`），其他 API 都不會重打。

---

## 二、活動卡片列表（#2 / #3）—— 最重要

`UIC:2812-2832` → `IMS.getActivityImage(platformId, user, imageType, activityCategoryId)`
- PC：`imageType = 4 (ACTIVITY)`；H5：`imageType = 5 (H5_ACTIVITY)`
- 每次呼叫列表時，都會清掉該登入者的角標快取（`IMS:475-481`）。

### 2.1 會出現在列表的 9 種活動來源

| 前綴 | 活動 | 資料表 | 後台設定 API | 受分類標籤過濾？ |
|---|---|---|---|---|
| `C` | 通用活動素材圖（優惠活動素材） | `image_manage` | `/api/admin/image/activityUpload`、`/activityUpdate`、`/updateStatus`、`/delete` | ✅ manage_type=1 |
| `B` | 消費活動（代理活動） | `agent_activity` + `activity_image` | `/api/admin/agentActivity/add\|update` | ✅ manage_type=4/5 |
| `L` | 虧損（負盈利）活動 | `agent_activity` + `activity_image` | `/api/admin/loseActivity/add\|update` | ✅ manage_type=4/5 |
| `R` | 充值活動 | `recharge_activity` + `activity_image` | `/api/admin/rechargeActivity/update` | ✅ manage_type=3 |
| `D` | 每日首充 | `daily_recharge_activity` | `/api/admin/dailyRechargeActivity/save` | ✅ manage_type=7 |
| `E` | 每日存款 | `daily_deposit_activity` | `/api/admin/dailyDepositActivity/save` | ✅ manage_type=9 |
| `F` | 新用戶首充 | `newbie_first_deposit_activity` | `/api/admin/newbieFirstDepositActivity/update` | ✅ manage_type=8 |
| `V` | X-BOMB（ActivityV2，template=X_BOMB） | `activity_v2_activity`、`activity_v2_list_config` | `/api/admin/activity-v2/activity/xbomb/save`、`/changeStatus` | ❌ **每個標籤都會出現** |
| （無 id） | 遊戲挑戰賽 v3 彙總卡（一張） | `game_challenge_config` / `_activity` / `_material` | `/api/admin/gameChallenge/config/save` 等 | ❌ **每個標籤都會出現** |
| `Y` | 預約活動（ActivityV2，template=RESERVATION） | `activity_v2_activity.promo_list_enabled`、`activity_v2_image` | `/api/admin/activity-v2/activity/save`、`/update-images` | ❌ **每個標籤都會出現** |

分類標籤的關聯表是 `activity_category_manage_relationship`。比對時要求 `manage_type` 相符、`manage_id` 等於活動 id，且 `activity_type` 字串包含 `,{categoryId},`（`IMS:774-793`）。

**不會出現在列表的：**
- ActivityV2 中 X_BOMB、RESERVATION 以外的 template（例如周卡）。
- 每日特別返水、每日返水加碼本身不會產生卡片。要讓它們出現，營運必須另外在 `image_manage` 建一張 C 卡，並把 `pending_claim_link` 設為 1 或 2，才會掛上角標。

### 2.2 各來源的出現條件

**C — image_manage**（`IMS:278-315`）
- `platform_id` 等於當前平台；`image_type` 為 4（PC）或 5（H5）。
- 時間：`showActivityByDate`（規則見 2.3）。
- `lang` 必須**完全等於**請求語系，沒有預設語系回退。
- `currency`：null 視為全幣別；有值時必須等於使用者幣別。訪客用平台預設幣別。
- `status`：null 視為顯示；有值時必須為 1。
- 不檢查 VIP、會員等級、註冊來源。

**B / L — agent_activity**（`AAS:795-908`）
- `activity_status = 1`，時間用 `showActivityByDate`。
- 訪客：只顯示 `active_agent = "*"` 且 `active_member_level = "*"` 的活動；虧損活動（L）例外，訪客一律看得到。
- 登入者：需符合 `active_agent`、`active_user`、上級、投注站規則其中一項，且會員層級符合 `active_member_level`。虧損活動不檢查這些。
- `vip_activity_config` 缺少對應的 VIP code 時會 NPE，觸發列表的例外分支（見 2.4）。

**R 充值**：`start_time` 不為 null，`activity_status = OPEN`，再過 `showActivityByDate`。沒有使用者限制。

**D 每日首充**
- DAO 只取 `activity_status=1 AND start_time<=now<=end_time`，快取 1 天。
- ⚠ 因為快取載入時就已用活動時間過濾，show 時間沒有作用。快取載入之後才開始的活動，要等快取失效（最長 1 天）才會出現。

**E 每日存款**：`activity_status=1`，且當下在 `start ~ end` 之間。只取第一筆，最多一張卡。不看 show 時間。

**F 新用戶首充**：`activity_status = OPEN` 加上 `showActivityByDate`。**不檢查是否為新用戶**，訪客也看得到。

**V X-BOMB**
- `activity_status = 1`、`begin_time <= now < display_end_time`。`display_end_time` 由系統計算：結束日隔天 12:00 再加 72 小時。
- `currency` 有值時需等於請求幣別。
- `activity_v2_list_config.enabled = 1`，且該端圖片（`pc_image` 或 `h5_image`）不為空。
- 一個平台只能啟用一個 X-BOMB。

**挑戰賽彙總卡**
- `game_challenge_config.status = 1`，且 `displayStartTime < now < displayEndTime`（兩者都不能是 null）。
- 至少一筆 `game_challenge_activity` 的 `status = 1` 且在顯示期間內。
- 若 `validBetEnabled = 1`：訪客看不到；登入者在前 N 天的有效投注必須大於 0 且不超過上限。

**Y 預約**
- 已啟用且 `begin_time <= now <= end_time`；template 為 RESERVATION；`promo_list_enabled = 1`（新建時預設 1）。
- 該端必須有圖片：`activity_v2_image` 中 `image_category=10`、`lang_code='default'`。
- 沒有幣別或使用者限制。

### 2.3 時間規則 `showActivityByDate`

位置：`DailyRechargeActivityServiceImpl.java:590-613`

- **show_start、show_end 都沒設**：看活動時間 `[start_time, end_time]`，null 的一端以 now 代替。
- **任一 show 時間有設**：只看 `[show_start, show_end]`，完全忽略活動時間。
- 四個欄位全空：永遠顯示。

### 2.4 排序與例外
- 排序：有待領（`pendingClaimCount > 0`）的排最前面，其餘依 `image_sort` **降序**，null 排最後（`IMS:468-471`）。
- ⚠ 從代理活動以後的任一步拋例外，會直接回傳已累積的結果（`IMS:459-462`）。此時 B/L、X-BOMB、挑戰賽、預約卡都可能消失，而且不會排序。

---

## 三、分類標籤（#1）

`UIC:3088-3097` → `activityCategoryCache`（1 天）→ `activity_category`

| 條件 | 證據 |
|---|---|
| `platform_id` 等於當前平台 | `ActivityCategoryDao.java:26` |
| `status = 1` | `ActivityCategoryDao.java:25` |
| 排序 `sort desc` | `ActivityCategoryDao.java:27` |
| 名稱依語系翻譯（i18n 表 `activity_category.name`），查不到用原名 | `UIC:3092-3095` |
| **不檢查類別底下有沒有活動**，空類別也會出現 | `UIC:3091` |

- 後台設定：`POST /api/admin/activity/editActivityCategory`，operatorType 1 新增、2 更新、3 刪除（硬刪除）。
- ⚠ 程式直接對快取物件 `setName`。某語系沒有翻譯時，可能拿到上一個請求語系的名稱。

---

## 四、待領角標（#4）

回傳值 = 活動卡片待領數加總 + 任務中心未領數（`questApiClientService.queryUnclaimedRewardCount`）

- 需要有效 token，否則 401。platformId 取自 token。
- 快取：`ActivityImagePendingClaimCountCache`（分散式），key 是 `platformId#userId#imageType#lang`，TTL **10 分鐘**。程式碼是 10 分鐘，EnumClass 的說明文字寫 1 分鐘，以程式碼為準。
- 未命中快取時，會以「不分類」的方式跑一次 #2/#3 的列表邏輯再加總。所以哪些活動算進角標，條件與列表完全相同。

| 卡片 | 怎麼算 |
|---|---|
| C 卡，`pending_claim_link=1`（每日特別返水） | `dailySpecialActivity.userInfo` 的 `pendingRewardAmount > 0` 則為 1 |
| C 卡，`pending_claim_link=2`（每日返水加碼） | 當日達標且未領的 level 數 |
| `L` 開頭 | `agent_activity_record` 中 `record_status=0`、`reward_amount>0`、且為本期，則為 1 |
| `B` 開頭 | 手動領取的消費活動，昨日投注或儲值算出 reward>0 且今日未領，則為 1 |
| 挑戰賽（link=3） | 進行中可領、未領的 level 數總和 |
| `V` X-BOMB | `XBombBadgeStore` 快取中的 mission + ticket 數 |
| `Y` 預約（link=5） | 可領筆數；沒有可領時，若開了提醒則為 1 |
| R / D / E / F / 其他 C 卡 | **不計算** |

⚠ B/L 只有**手動領取（send_way=MANUAL）**的活動才會有角標；自動派發的活動永遠沒有角標。

---

## 五、PC 熱門活動 Swiper（#5 rewardCenterActivityList）

`reward_center_activity` 表，後台 `/api/admin/rewardCenterActivity/add|update|delete`

| 條件 | 有無 |
|---|---|
| `platform_id` | ✅ |
| `status = 1` | ✅ 唯一的業務條件 |
| 時間、語系、幣別、終端、使用者 | ❌ 都沒有 |
| 排序 | `sort` 升序 |

- 跟活動的關聯**只靠後台手填的 `jump_url`**，後端不會檢查目標活動是否還開著。
- `imageHost` 在前台永遠是 null，前端自己拼接 `resServerHost`。
- ⚠ 依程式碼推論、未實測：`sort` 允許為 null，但排序時沒處理 null，有 null 時整支 API 會 NPE。
- 快取 `rewardCenterActivityCache`，1 天，後台異動後會通知刷新。

---

## 六、promotions（#6，PC 用來顯示「每日返水」卡片）

固定回傳順序：`daily_rebate` → `rebate_sports` → `pay_day` → `rebate_negative` → `daily_first_deposit_{id}` → `daily_deposit_{id}`。任一區塊拋例外，該項目就不出現。

前端只用到 `daily_rebate`：

| 欄位 | 來源 |
|---|---|
| 是否出現 | 該平台在 `consume_activity` 有資料即出現，與 status 無關 |
| `isActive` | `status=1`，且當下在 `start_time ~ end_time` 之間（與登入無關） |
| `rebateJumpIdPC` / `rebateJumpIdH5` | `image_manage` 中 `image_type=4/5` 且 `is_rebate=1` 的第一筆，值為 `"C"+id`。**不看該素材的 status、語系、時間** |

- 後台：每日返水設定 `POST /api/admin/consumeActivity/save`；跳轉素材是在優惠活動素材上勾選「每日返水」（`is_rebate`），每個平台每種 image_type 只能有一筆。

---

## 七、簽到、獎金日曆、每日特別返水

### 7.1 normalSignStatus（#7）
- 表：`normal_sign_activity_config`（後台 `/api/admin/normalSignActivity/update`）、`normal_sign_activity_record`、`new_user_sign_record`。

| 情況 | 回傳 |
|---|---|
| 沒有 config，或 `activity_status ≠ 1` | `activityStatus=2`（關），前端不顯示簽到 |
| 新手 7 日簽到參與中、未簽滿、且註冊未滿 14 天 | `activityStatus=3`，前端提示「請先完成新手簽到」 |
| 今天未簽 | `actionType=1`，前端顯示紅點 |
| 今天已簽 | `actionType=2` |

- 沒有時間窗、終端、KYC、VIP 檢查。簽到天數週期 = `reward_config` 陣列長度。
- ⚠ 這支是查詢，但新手簽到已滿 7 天時會順便把紀錄改成「結束」並寫回 DB。

### 7.2 bonus-calendar（#8）
- 表：`activity_bonus_calendar`。**只依 user_id 查**，不看平台，也不看活動開關。
- 寫入來源：Payday（activity_id=1）、週負盈利返水（101）、週體育返水（102）。
- `pendingTotalBonus`：
  - `/month`：該使用者全部未領、且日期 ≥ 今天的總和，與查詢的月份無關。
  - `/recent`：只算今天起 10 天內。
- ⚠ 來源活動關閉後，未來的日曆獎金仍會顯示並計入總額。

### 7.3 dailySpecialActivity/userInfo（#9）
- 表：`daily_special_activity_config`，每個平台一筆。後台 `/api/admin/dailySpecialActivity/saveConfig`。
- `status=1` 且在 `start_time ~ end_time` 內，才會回傳有內容的資料；否則回傳空 VO。
- 有 `@AccessLimit(150ms)`，以及全站 `@MethodAccessLimit`（預設每秒 200 次，可用 config `DailySpecialAccessLimit` 覆寫）。

---

## 八、任務、FreeSpin、優惠券、積分商城、VIP

| API | 後端結論 |
|---|---|
| #10 `quest/info`、`quest/guest/info` | **不在本機 repo**，屬獨立的任務系統服務（Swagger 在 `quest-api-doc.cxsport.net`）。本機只能確認開關 `questSystemOpen`（`ConfigKey.java:1795`，預設 0）。分類、conditionType、deliverStatus：**not verified** |
| #14 `product/index` | 同上，屬任務系統或積分商城服務。開關 `pointSystemOpen`：**not verified** 其內部篩選 |
| #11 `freeSpin/queryListFront` | 表 `free_spin_config`，只依 platform_id 查。⚠ **沒有過濾 status**：後台「刪除」是把 status 改成 0 的軟刪除，但該筆仍會出現在前台（`FreeSpinConfigServiceImpl.java:271-274` 設了 query.status 卻沒有使用）。快取 1 分鐘 + 1 天 |
| #12 `freeSpin/queryCouponTotalCount` | `free_spin_record` 依 user_id 統計。未使用 = `receive_status=0` 且未過期 |
| #13 `coupon-system/queryAll` | `coupon_record` 依 user_id 查，回傳所有狀態；過期的券回傳時改成狀態 3。不檢查 `couponSystemOpen` |
| #15 `vip/user`、`vip/detail` | `a_activity`（type=8）、`user_level_config_v2`（enable=1）、`a_activity_user_level` 等。後台 `/api/admin/userLevelConfigV2`、`/api/admin/activity/save/userLevel` |

開關 `questSystemOpen`、`pointSystemOpen`、`couponSystemOpen`、`freeSpinSwitch` 都是**前端依 config 決定要不要顯示入口**。#11–#13 的後端不會因為開關關閉而擋下請求。

---

## 九、調查中發現的疑似問題（皆未修改）

1. `freeSpin/queryListFront` 不過濾 status，軟刪除的配置仍會出現。
2. `activityImageList` 中段只要拋一次例外，就會漏掉 B/L、X-BOMB、挑戰賽、預約卡。
3. 每日首充（D）的 show 時間被快取載入時的過濾抵銷，新活動最長要等 1 天才會出現。
4. `activityCategoryList` 直接改快取物件的名稱，可能造成語系串台。
5. `rewardCenterActivityList` 的 `sort` 為 null 時可能 NPE（依程式碼推論，未實測）。
6. 獎金日曆不分平台，也不檢查來源活動是否開啟。
7. B/L 的自動派發活動永遠不會有角標。
8. 角標快取 TTL 的說明文字（1 分鐘）與程式碼（10 分鐘）不一致。

## 十、未驗證
- 任務系統、積分商城服務（不在本機）。
- `DailyDepositActivityServiceImpl.resolveActive` 的過濾條件、`rebate_sports` / `rebate_negative` 的快取 TTL。
- `DailyRebateBoostActivityServiceImpl` 角標計數迴圈的後半段。
- Kafka 快取失效在各節點的實際行為。
