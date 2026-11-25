# app-updates

Automatic update feeds for Reynold Kajiwara's Mac apps, read by each app's built-in updater (Sparkle 2).

| App | Update feed | Downloads |
| --- | --- | --- |
| Sukkiri | `sukkiri/appcast.xml` | `sukkiri/` |
| Benri | `benri/appcast.xml` | `benri/` |
| Kocchi | `kocchi/appcast.xml` | `kocchi/` |

Each update is notarized by Apple and signed with Reynold's own key (EdDSA); the apps refuse any update
without that signature. The source code is not here; it stays in private repositories.
