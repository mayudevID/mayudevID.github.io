# Designing Reliable Push Notifications in Flutter with Firebase Cloud Messaging

“Reliable” notifications begin with a useful design, not a promise of delivery. A push message depends on service configuration, network conditions, user permission, application state, and operating-system policy. Treat the push as a cue to refresh or open relevant data; keep the server and app able to recover when a message is delayed or never handled.

## Separate delivery, display, and navigation

FCM notification and data payloads serve different purposes, and mixed payload behavior depends on whether the app is active. In Flutter, handle foreground events through `FirebaseMessaging.onMessage`. A notification received in the foreground is not displayed visibly by default on Android or iOS; configure platform presentation only when it fits the product. Background work uses a top-level `onBackgroundMessage` handler. Keep that handler short and independent of widget state.

Handle a notification tap separately from receipt. `getInitialMessage()` covers an app opened from a terminated state; `onMessageOpenedApp` covers a tap that resumes a backgrounded app. Validate the payload and authorization before navigating. A deep link should identify the requested destination, while the destination still loads current data from its trusted source.

## Account for platform and permission differences

Ask for notification permission when the user can understand the value. Android 13 and later and Apple platforms require permission for notification presentation. On iOS, configure Push Notifications and the required background modes, and connect APNs credentials to Firebase. On Android, verify the notification channel and the app's target SDK behavior. A denied permission should leave core app functions usable.

## Keep registration current and test state transitions

Associate a device registration with the signed-in account on the server, update it when the registration changes, and remove or invalidate the association on sign-out according to product policy. Never treat a registration identifier as an authentication credential. Test foreground, background, terminated, permission-denied, token-change, sign-out, and notification-tap cases on real platform configurations. Force-stop and swipe-away behavior can differ from ordinary backgrounding.

FCM does not guarantee that every message will reach or be shown on a device. Design important data workflows to reconcile with the server on app start or resume, and inspect delivery reporting when diagnosing a delivery problem.

### Further reading

- [Receive messages in Flutter apps](https://firebase.google.com/docs/cloud-messaging/flutter/receive-messages)
- [Get started with FCM in Flutter](https://firebase.google.com/docs/cloud-messaging/flutter/get-started)
- [FCM message types](https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type)

This draft is general guidance. The exact operating-system, SDK, and app-configuration matrix must be checked again before publication; no project-specific notification implementation is claimed.
