# Managing Offline Data and Application State in Flutter

An offline indicator answers only whether a device appears connected to a network. It cannot prove that a particular API is reachable or that a user may still access a protected resource. A useful offline design decides which data can be read locally, which changes can be queued, and when the app must ask the server again.

## Name the source of each state

Separate transient UI state—such as a selected tab—from remote account data and durable local data. For each screen, define whether the first render uses cache, waits for the network, or combines both. Show when cached information was last refreshed if freshness matters. Keep loading, empty, stale, success, and failure states distinct so an unavailable request is not mistaken for an empty result.

## Choose persistence and synchronization deliberately

Use lightweight key-value storage for preferences and a structured database when data has relationships or needs queries. Flutter's offline-first guidance describes repository strategies for combining local and remote sources; the right policy depends on the data. Decide which operations are safe to retry, how duplicate submissions are prevented, and what happens when the server rejects an offline change. For conflicting edits, define a merge or user-resolution rule instead of silently overwriting one version.

## Respect authentication and data ownership

Scope local records to the signed-in account and clear or isolate them on account changes. Avoid showing one user's cached data after another user signs in. Expired credentials, revoked access, and server-side deletion can invalidate local assumptions; decide how the app revalidates before sensitive actions.

## Test without trusting connectivity callbacks

Test airplane mode, captive portals, DNS failures, slow or interrupted requests, process restarts, and simultaneous server changes. Connectivity signals are hints; an actual request can still fail. Test that retry is bounded and idempotent, that queued work is visible, and that users can recover from a conflict. Check migration and backup behavior for locally persisted data as its schema evolves.

### Further reading

- [Flutter offline-first support](https://docs.flutter.dev/app-architecture/design-patterns/offline-first)
- [Flutter data layer case study](https://docs.flutter.dev/app-architecture/case-study/data-layer)
- [Persistent SQL storage architecture](https://docs.flutter.dev/app-architecture/design-patterns/sql)

This is general design guidance, not a description of how any listed portfolio project handles offline synchronization.
