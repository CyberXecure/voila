# v0.8.34a Tester package rebuild final-main cleanup fix — no share/no delivery

## Purpose

This follow-up fixes the v0.8.34 final-main validation cleanup path on Windows.

The v0.8.34 package rebuild was merged, but the final-main rerun hit a Windows long-path cleanup failure while deleting the existing staging folder.

## Fix

The tester package rebuild check now removes the staging folder using the existing Windows extended path helper.

## Boundary

This milestone changes only validation/check behavior.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not change Course Tools.

It does not change Study behavior.

It does not write Progress.

It does not mark answers.

It does not create a share.

It does not copy to OneDrive.

It does not deliver anything.

It does not distribute anything.

## Expected result

The v0.8.34 package rebuild check can be rerun from final main cleanly.

The local ZIP may be rebuilt.

No share, no OneDrive copy, no delivery, and no public release are created.
