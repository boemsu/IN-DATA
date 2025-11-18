# 0. 패키지 로드 
install.packages("tidyverse")
install.packages("jsonlite")
library(tidyverse)

# 1. 데이터 불러오기
df_raw <- read_csv("inha_populartimes_MAX_1200m.csv")

glimpse(df_raw)
head(df_raw)

# 2. 전처리 
df_clean <- df_raw %>%
  mutate(
    시간_numeric = as.numeric(str_remove(시간대, "시")),
    요일 = factor(요일,
                levels = c("월","화","수","목","금","토","일"),
                ordered = TRUE),
    평균혼잡도 = as.numeric(평균혼잡도)
  ) %>%
  drop_na(평균혼잡도, 시간_numeric)

glimpse(df_clean)

# 3. 요일×시간대 Heatmap 
heat_df <- df_clean %>%
  group_by(요일, 시간_numeric) %>%
  summarise(평균혼잡도 = mean(평균혼잡도), .groups = "drop")

ggplot(heat_df, aes(x = 시간_numeric, y = 요일, fill = 평균혼잡도)) +
  geom_tile() +
  scale_fill_gradient(low = "white", high = "red") +
  labs(
    title = "인하대 상권 요일·시간대 평균 혼잡도",
    x = "시간대",
    y = "요일",
    fill = "평균 혼잡도(0~100)"
  ) +
  theme_minimal()

# 4. 가게별·요일별 피크시간 도출 
peak_df <- df_clean %>%
  group_by(Place_ID, 가게명, 요일) %>%
  slice_max(order_by = 평균혼잡도, n = 1, with_ties = FALSE) %>%
  ungroup()

head(peak_df)

# 피크 시간대 분포 히스토그램
ggplot(peak_df, aes(x = 시간_numeric)) +
  geom_histogram(binwidth = 1, boundary = 0, closed = "left") +
  scale_x_continuous(breaks = 0:23) +
  labs(
    title = "가게별 피크 시간대 분포",
    x = "피크 시간대(시)",
    y = "가게 수"
  ) +
  theme_minimal()

# 5. 가게별 혼잡 특성 Feature 생성
features <- df_clean %>%
  mutate(
    주말 = 요일 %in% c("토","일"),
    점심 = 시간_numeric >= 11 & 시간_numeric <= 14,
    저녁 = 시간_numeric >= 18 & 시간_numeric <= 21
  ) %>%
  group_by(Place_ID, 가게명) %>%
  summarise(
    avg_pop_all = mean(평균혼잡도),
    max_pop = max(평균혼잡도),
    avg_lunch = mean(평균혼잡도[점심], na.rm = TRUE),
    avg_dinner = mean(평균혼잡도[저녁], na.rm = TRUE),
    avg_weekday = mean(평균혼잡도[!주말], na.rm = TRUE),
    avg_weekend = mean(평균혼잡도[주말], na.rm = TRUE),
    .groups = "drop"
  )

glimpse(features)

library(dplyr)
library(ggplot2)

# 6-1. 군집에 쓸 숫자형 변수 정리 
features_model <- features %>%
  mutate(
    avg_pop_all  = as.numeric(avg_pop_all),
    max_pop      = as.numeric(max_pop),
    avg_lunch    = as.numeric(avg_lunch),
    avg_dinner   = as.numeric(avg_dinner),
    avg_weekday  = as.numeric(avg_weekday),
    avg_weekend  = as.numeric(avg_weekend)
  ) %>%
  # NA는 0으로 통일 (해당 구간에 데이터 없을 때)
  mutate(
    across(
      c(avg_pop_all, max_pop, avg_lunch, avg_dinner, avg_weekday, avg_weekend),
      ~ ifelse(is.na(.x), 0, .x)
    )
  )

# 6-2. kmeans에 넣을 행렬 만들기 
num_mat <- features_model %>%
  select(avg_pop_all, max_pop, avg_lunch, avg_dinner, avg_weekday, avg_weekend) %>%
  as.matrix()

# 6-3. 혹시 모를 NaN / Inf도 전부 0으로 강제 =
num_mat[!is.finite(num_mat)] <- 0

# 6-4. K-means 실행
set.seed(42)
k3 <- kmeans(num_mat, centers = 3, nstart = 20)

# 6-5. 클러스터 결과를 features_model에 붙이기 
features_model$cluster <- factor(k3$cluster)

# 이후 분석에 쓸 메인 객체를 features로 업데이트
features <- features_model

# 6-6. 군집별 요약 통계 
cluster_summary <- features %>%
  group_by(cluster) %>%
  summarise(
    n_store      = n(),
    avg_pop_all  = mean(avg_pop_all),
    max_pop      = mean(max_pop),
    avg_lunch    = mean(avg_lunch),
    avg_dinner   = mean(avg_dinner),
    avg_weekday  = mean(avg_weekday),
    avg_weekend  = mean(avg_weekend),
    .groups = "drop"
  )

cluster_summary


# 6-7. 군집별 전체 평균 혼잡도 막대그래프
library(ggplot2)

ggplot(cluster_summary, aes(x = cluster, y = avg_pop_all, fill = cluster)) +
  geom_col() +
  labs(
    title = "군집별 전체 평균 혼잡도",
    x = "클러스터",
    y = "평균 혼잡도(0~100)"
  ) +
  theme_minimal()

# 첨부한 그래프
#1. 요일·시간대별 평균 혼잡도 히트맵
library(dplyr)
library(ggplot2)

heat_df <- df_clean %>%
  group_by(요일, 시간_numeric) %>%
  summarise(평균혼잡도 = mean(평균혼잡도), .groups = "drop")

ggplot(heat_df, aes(x = 시간_numeric, y = 요일, fill = 평균혼잡도)) +
  geom_tile() +
  scale_fill_gradient(low = "white", high = "red") +
  scale_x_continuous(breaks = 0:23) +
  labs(
    title = "요일·시간대별 평균 혼잡도 히트맵",
    x = "시간대",
    y = "요일",
    fill = "평균 혼잡도(0~100)"
  ) +
  theme_minimal()


#2. 가게별 피크 시간대 분포 히스토그램
library(dplyr)
library(ggplot2)

peak_df <- df_clean %>%
  group_by(Place_ID, 가게명) %>%
  slice_max(order_by = 평균혼잡도, n = 1, with_ties = FALSE) %>%
  ungroup()

ggplot(peak_df, aes(x = 시간_numeric)) +
  geom_histogram(binwidth = 1, boundary = 0, closed = "left") +
  scale_x_continuous(breaks = 0:23) +
  labs(
    title = "가게별 최대 혼잡도 발생 시간대 분포",
    x = "피크 시간대(시)",
    y = "매장 수"
  ) +
  theme_minimal()


#3. 클러스터별 평균 혼잡도 막대그래프
library(dplyr)
library(ggplot2)

cluster_summary <- features %>%
  group_by(cluster) %>%
  summarise(
    평균혼잡도_군집 = mean(avg_pop_all, na.rm = TRUE),
    n_store = n(),
    .groups = "drop"
  )

ggplot(cluster_summary, aes(x = cluster, y = 평균혼잡도_군집, fill = cluster)) +
  geom_col() +
  labs(
    title = "클러스터별 평균 혼잡도 비교",
    x = "클러스터",
    y = "평균 혼잡도(0~100)"
  ) +
  theme_minimal()



#4. 특정 매장 시간대 패턴 라인 그래프
library(dplyr)
library(ggplot2)

target_store <- "오월의유부"
store_df <- df_clean %>%
  filter(가게명 == "오월의유부")

ggplot(store_df, aes(x = 시간_numeric, y = 평균혼잡도,
                     color = 요일, group = 요일)) +
  geom_line(size = 1) +
  scale_x_continuous(breaks = 0:23) +
  labs(
    title = paste0("시간대별 혼잡 패턴 - ", "오월의유부"),
    x = "시간대",
    y = "혼잡도(0~100)"
  ) +
  theme_minimal()

# 7. Flask 연동을 위한 JSON 파일 저장 (추가된 코드)
library(jsonlite)
library(dplyr)

# 지도 마커에 필요한 '주소'와 '가게명'을 features_model에 병합
store_info <- df_clean %>%
  select(Place_ID, 가게명, 주소) %>%
  distinct()

features_model_final <- features_model %>%
  left_join(store_info, by = c("Place_ID", "가게명"))

# 7-1. 식당 목록 및 대표 혼잡도 (F-1, F-2용) 저장
# (추가: Place_ID를 'store_id'로, 가게명을 'store_name'으로 변경하여 API 명세와 일치시킴)
features_json_output <- features_model_final %>%
  rename(store_id = Place_ID, store_name = 가게명, address = 주소) %>%
  select(store_id, store_name, address, avg_pop_all, max_pop, cluster)

# 실제로 지도 SDK를 사용하려면 여기에 위도/경도(latitude/longitude) 필드가 추가되어야 합니다.
write_json(features_json_output, "features_model.json", pretty = TRUE)


# 7-2. 요일/시간대 상세 혼잡도 (F-3용) 저장
# Place_ID, 요일, 시간_numeric, 평균혼잡도 등을 포함
write_json(df_clean, "df_clean_pop.json", pretty = TRUE)



# --- 7. Flask 연동을 위한 JSON 파일 저장 ---

# 7-1. 식당 목록 및 대표 혼잡도 (F-1, F-2용) 저장
# 주소(address) 정보를 features_model에 병합합니다.
store_info <- df_clean %>%
  select(Place_ID, 가게명, 주소) %>%
  distinct()

features_model_final <- features_model %>%
  left_join(store_info, by = c("Place_ID", "가게명"))

features_json_output <- features_model_final %>%
  rename(store_id = Place_ID, store_name = 가게명, address = 주소) %>%
  select(store_id, store_name, address, avg_pop_all, max_pop, cluster)

write_json(features_json_output, "features_model.json", pretty = TRUE)


# 7-2. 요일/시간대 상세 혼잡도 (F-3용) 저장
write_json(df_clean, "df_clean_pop.json", pretty = TRUE)