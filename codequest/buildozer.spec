[app]
title = Code Quest
package.name = codequest
package.domain = org.codequest

source.dir = .
source.include_exts = py,png,wav,ttf
source.exclude_dirs = tests, bin, .buildozer, .github, __pycache__
version = 1.0.0

# Kivy 2.3.0 and pyjnius (used for vibration) are pulled in by these two names.
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
android.presplash_color = #0e1128

# Haptics need this permission.
android.permissions = VIBRATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

# Known-good python-for-android release for Kivy 2.3.0 + Python 3.11
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0
