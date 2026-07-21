# v0.8.34b Tester package rebuild long-path helper order fix — no share/no delivery

## Purpose

This follow-up fixes the v0.8.34/v0.8.34a final-main validation on Windows.

The previous cleanup patch called `win_extended_path(staging_dir)` before the helper was defined during module execution.

## Fix

The tester package rebuild check now defines `win_extended_path` before the package staging cleanup block.

## Boundary

This milestone changes validation/check behavior only.

It does not modify `services/api/web_app.py`.

It does not add a route.

It does not add a POST endpoint.

It does not change Study behavior.

It does not write Progress.

It does not mark answers.

It does not create a share.

It does not copy to OneDrive.

It does not deliver anything.

It does not distribute anything.

It does not create a public release.

## Expected result

The v0.8.34 tester package rebuild check can be rerun from final main cleanly.

The local ZIP may be rebuilt only under `D:\dev\release-assets`.

No share, no OneDrive copy, no delivery, and no public release are created.
