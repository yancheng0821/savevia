import UIKit
import Capacitor
import WebKit

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // Configure webview settings after it's loaded
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.configureWebView()
        }

        return true
    }

    private func configureWebView() {
        guard let rootVC = window?.rootViewController as? CAPBridgeViewController,
              let webView = rootVC.webView else {
            // Retry if webView not ready
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                self.configureWebView()
            }
            return
        }

        // Enable bounce effect
        webView.scrollView.bounces = true
        webView.scrollView.alwaysBounceVertical = true

        // Enable swipe back/forward gesture for navigation
        webView.allowsBackForwardNavigationGestures = true

        // Set background color to match app theme
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 1.0, green: 0.988, blue: 0.961, alpha: 1.0) // #FFFCF5
        webView.scrollView.backgroundColor = UIColor(red: 1.0, green: 0.988, blue: 0.961, alpha: 1.0)

        // Disable all loading indicators and spinners
        disableLoadingIndicators(in: webView)

        // Observe for any new subviews being added
        webView.scrollView.subviews.forEach { subview in
            if String(describing: type(of: subview)).contains("Indicator") ||
               String(describing: type(of: subview)).contains("Refresh") {
                subview.isHidden = true
                subview.removeFromSuperview()
            }
        }

    }

    private func disableLoadingIndicators(in view: UIView) {
        for subview in view.subviews {
            // Hide any activity indicators
            if let indicator = subview as? UIActivityIndicatorView {
                indicator.stopAnimating()
                indicator.isHidden = true
                indicator.removeFromSuperview()
            }

            // Hide refresh controls
            if let refreshControl = subview as? UIRefreshControl {
                refreshControl.endRefreshing()
                refreshControl.removeFromSuperview()
            }

            // Check class name for system indicators
            let className = String(describing: type(of: subview))
            if className.contains("ActivityIndicator") ||
               className.contains("RefreshControl") ||
               className.contains("_UIActivityIndicator") {
                subview.isHidden = true
                subview.removeFromSuperview()
            }

            // Recursively check subviews
            disableLoadingIndicators(in: subview)
        }
    }

    func applicationWillResignActive(_ application: UIApplication) {
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
    }

    func applicationWillTerminate(_ application: UIApplication) {
    }

    func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool {
        return ApplicationDelegateProxy.shared.application(app, open: url, options: options)
    }

    func application(_ application: UIApplication, continue userActivity: NSUserActivity, restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
        return ApplicationDelegateProxy.shared.application(application, continue: userActivity, restorationHandler: restorationHandler)
    }

}
