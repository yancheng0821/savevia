package com.savevia.app;

import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;

import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Enable edge-to-edge display
        setupEdgeToEdge();
    }

    private void setupEdgeToEdge() {
        Window window = getWindow();

        // Enable edge-to-edge
        WindowCompat.setDecorFitsSystemWindows(window, false);

        // Set status bar and navigation bar colors
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            window.setStatusBarColor(android.graphics.Color.parseColor("#FFFCF5"));
            window.setNavigationBarColor(android.graphics.Color.parseColor("#FFFCF5"));
        }

        // Configure status bar icons to be dark (for light background)
        WindowInsetsControllerCompat windowInsetsController =
            WindowCompat.getInsetsController(window, window.getDecorView());
        if (windowInsetsController != null) {
            // Dark icons for light background
            windowInsetsController.setAppearanceLightStatusBars(true);
            windowInsetsController.setAppearanceLightNavigationBars(true);
        }

        // Support display cutout (notch, punch-hole, etc.)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            WindowManager.LayoutParams layoutParams = window.getAttributes();
            layoutParams.layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
            window.setAttributes(layoutParams);
        }
    }
}
