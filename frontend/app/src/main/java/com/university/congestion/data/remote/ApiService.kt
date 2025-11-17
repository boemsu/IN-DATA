package com.university.congestion.data.remote

import com.university.congestion.data.remote.dto.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    /**
     * 식당 목록 조회
     */
    @GET("stores")
    suspend fun getStores(
        @Query("latitude") latitude: Double? = null,
        @Query("longitude") longitude: Double? = null,
        @Query("radius") radius: Double? = null
    ): Response<ApiResponse<List>>

    /**
     * 식당 상세 조회
     */
    @GET("stores/{storeId}")
    suspend fun getStore(
        @Path("storeId") storeId: Int
    ): Response<ApiResponse>

    /**
     * 식당 혼잡도 조회
     */
    @GET("stores/{storeId}/congestion")
    suspend fun getStoreCongestion(
        @Path("storeId") storeId: Int,
        @Query("target_time") targetTime: String? = null
    ): Response<ApiResponse>

    /**
     * 피크 시간대 조회
     */
    @GET("stores/{storeId}/peak-times")
    suspend fun getPeakTimes(
        @Path("storeId") storeId: Int
    ): Response<ApiResponse<List>>

    /**
     * 방문 의사 등록
     */
    @POST("visits/intentions")
    suspend fun registerVisitIntention(
        @Body request: VisitIntentionRequest
    ): Response<ApiResponse>

    /**
     * 실제 방문 기록 (진입)
     */
    @POST("visits/actual")
    suspend fun recordActualVisit(
        @Body request: ActualVisitRequest
    ): Response<ApiResponse>

    /**
     * 방문 종료 기록 (이탈)
     */
    @POST("visits/actual/exit")
    suspend fun recordVisitExit(
        @Body request: VisitExitRequest
    ): Response<ApiResponse>
}