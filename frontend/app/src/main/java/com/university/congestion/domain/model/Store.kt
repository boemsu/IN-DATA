package com.university.congestion.domain.model

data class Store(
    val id: Int,
    val placeId: String,
    val name: String,
    val address: String,
    val latitude: Double,
    val longitude: Double,
    val category: String?,
    val openingHours: Map?,
    val phone: String?
)

data class StoreCongestion(
    val storeId: Int,
    val storeName: String,
    val predictedCongestion: Int,      // R 모델 예측값 (0-100)
    val realtimeCongestion: Int,       // 실시간 혼잡도 (0-100)
    val currentVisitors: Int,          // 현재 체류 중
    val expectedVisitors: Int,         // 방문 예정
    val timestamp: String,
    val congestionLevel: String        // "여유", "보통", "혼잡", "매우혼잡"
)

data class VisitIntention(
    val userId: String,
    val storeId: Int,
    val intendedTime: String,          // ISO 8601 format
    val intendedPeople: Int
)

data class ActualVisit(
    val userId: String,
    val storeId: Int,
    val entryTime: String,
    val intendedPeople: Int
)