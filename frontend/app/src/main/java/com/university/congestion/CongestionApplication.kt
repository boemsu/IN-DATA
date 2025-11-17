package com.university.congestion

import android.app.Application
import timber.log.Timber

class CongestionApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Timber 초기화 (로깅)
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }

        Timber.d("Application 시작")
    }
}