package com.university.congestion.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * 공통 API 응답 형식
 */
data class ApiResponse(
    @SerializedName("success")
    val success: Boolean,

    @SerializedName("data")
    val data: T? = null,

    @SerializedName("error")
    val error: ApiError? = null
)

data class ApiError(
    @SerializedName("code")
    val code: String,

    @SerializedName("message")
    val message: String,

    @SerializedName("details")
    val details: Map? = null
)

// DTO 클래스들
data class StoreDto(
    @SerializedName("id") val id: Int,
    @SerializedName("place_id") val placeId: String,
    @SerializedName("name") val name: String,
    @SerializedName("address") val address: String,
    @SerializedName("latitude") val latitude: Double,
    @SerializedName("longitude") val longitude: Double,
    @SerializedName("category") val category: String?,
    @SerializedName("opening_hours") val openingHours: Map?,
    @SerializedName("phone") val phone: String?
)

data class StoreCongestionDto(
    @SerializedName("store_id") val storeId: Int,
    @SerializedName("store_name") val storeName: String,
    @SerializedName("predicted_congestion") val predictedCongestion: Int,
    @SerializedName("realtime_congestion") val realtimeCongestion: Int,
    @SerializedName("current_visitors") val currentVisitors: Int,
    @SerializedName("expected_visitors") val expectedVisitors: Int,
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("congestion_level") val congestionLevel: String
)

data class PeakTimeDto(
    @SerializedName("place_id") val placeId: String,
    @SerializedName("weekday") val weekday: String,
    @SerializedName("peak_hour") val peakHour: Int,
    @SerializedName("peak_congestion") val peakCongestion: Float
)

data class VisitIntentionRequest(
    @SerializedName("user_id") val userId: String,
    @SerializedName("store_id") val storeId: Int,
    @SerializedName("intended_time") val intendedTime: String,
    @SerializedName("intended_people") val intendedPeople: Int
)

data class VisitIntentionResponse(
    @SerializedName("intention_id") val intentionId: Int,
    @SerializedName("tracking_started") val trackingStarted: Boolean,
    @SerializedName("message") val message: String
)

data class ActualVisitRequest(
    @SerializedName("user_id") val userId: String,
    @SerializedName("store_id") val storeId: Int,
    @SerializedName("entry_time") val entryTime: String,
    @SerializedName("intended_people") val intendedPeople: Int
)

data class ActualVisitResponse(
    @SerializedName("visit_id") val visitId: Int,
    @SerializedName("is_duplicate") val isDuplicate: Boolean,
    @SerializedName("message") val message: String
)

data class VisitExitRequest(
    @SerializedName("user_id") val userId: String,
    @SerializedName("store_id") val storeId: Int,
    @SerializedName("exit_time") val exitTime: String
)

data class VisitExitResponse(
    @SerializedName("visit_id") val visitId: Int,
    @SerializedName("stay_time_minutes") val stayTimeMinutes: Int?,
    @SerializedName("is_valid_visit") val isValidVisit: Boolean,
    @SerializedName("message") val message: String
)