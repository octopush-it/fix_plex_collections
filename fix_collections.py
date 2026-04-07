#!/usr/bin/env python3
"""
Plex Collection Cleanup Script
================================
Deletes collections that:
  - Were auto-created by the Plex metadata agent, OR
  - Contain fewer than MIN_ITEMS items (movies/episodes)

Usage:
  1. Set PLEX_URL and PLEX_TOKEN below (or use environment variables).
  2. Run in dry-run mode first (DRY_RUN = True) to preview what will be deleted.
  3. When satisfied, set DRY_RUN = False and run again to actually delete.

Finding your Plex token:
  https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
"""

import os
import sys

# ── Configuration ─────────────────────────────────────────────────────────────

PLEX_URL   = os.getenv("PLEX_URL",   "http://localhost:32400")   # e.g. http://192.168.1.10:32400
PLEX_TOKEN = os.getenv("PLEX_TOKEN", "TOKEN_HERE")

# Minimum number of items a collection must have to be kept.
# Collections with FEWER than this number will be flagged for deletion.
MIN_ITEMS = 4

# Set to True to preview only. Set to False to actually delete.
DRY_RUN = True 

# Which library types to scan. Options: "movie", "show", or both.
LIBRARY_TYPES = ["movie"]  # Change to ["movie", "show"] to include TV libraries

# ── Script ────────────────────────────────────────────────────────────────────

try:
    from plexapi.server import PlexServer
except ImportError:
    print("ERROR: plexapi is not installed.")
    print("Install it with:  pip install plexapi")
    sys.exit(1)


def get_libraries(plex, types):
    """Return all libraries matching the given type(s)."""
    return [lib for lib in plex.library.sections() if lib.type in types]


def should_delete(collection):
    """
    Return (True, reason) if the collection should be deleted, else (False, "").

    Conditions (either is enough):
      1. Created by Plex agent (auto-generated metadata collection)
      2. Has fewer than MIN_ITEMS items
    """
    reasons = []

    # --- Condition 1: auto-created by Plex agent ---
    # plexapi exposes this as collection.createdByAgent (bool)
    # Fallback: check the raw attribute if the property isn't available
    try:
        agent_created = bool(collection.createdByAgent)
    except AttributeError:
        # Older plexapi versions: inspect raw data
        agent_created = collection._data.attrib.get("createdByAgent", "0") == "1"

    if agent_created:
        reasons.append("auto-created by Plex agent")

    # --- Condition 2: fewer than MIN_ITEMS items ---
    try:
        item_count = collection.childCount
    except AttributeError:
        item_count = len(collection.items())

    if item_count < MIN_ITEMS:
        reasons.append(f"only {item_count} item(s) (minimum is {MIN_ITEMS})")

    if reasons:
        return True, " + ".join(reasons)
    return False, ""


def main():
    print(f"\n{'='*60}")
    print(f"  Plex Collection Cleanup")
    print(f"  Mode: {'DRY RUN (no changes will be made)' if DRY_RUN else '⚠️  LIVE — collections will be DELETED'}")
    print(f"  Server: {PLEX_URL}")
    print(f"  Min items to keep: {MIN_ITEMS}")
    print(f"{'='*60}\n")

    if PLEX_TOKEN == "YOUR_TOKEN_HERE":
        print("ERROR: Please set your PLEX_TOKEN before running this script.")
        print("  Edit the PLEX_TOKEN variable at the top of the file, or")
        print("  run with:  PLEX_TOKEN=yourtoken python plex_cleanup_collections.py")
        sys.exit(1)

    # Connect
    print(f"Connecting to Plex at {PLEX_URL} ...")
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except Exception as e:
        print(f"ERROR: Could not connect to Plex: {e}")
        sys.exit(1)
    print(f"Connected as: {plex.myPlexUsername or 'unknown'}\n")

    libraries = get_libraries(plex, LIBRARY_TYPES)
    if not libraries:
        print(f"No libraries found with types: {LIBRARY_TYPES}")
        sys.exit(0)

    total_flagged = 0
    total_deleted = 0
    total_kept    = 0

    for lib in libraries:
        print(f"── Library: {lib.title} ({lib.type}) ──────────────────────")
        try:
            collections = lib.collections()
        except Exception as e:
            print(f"  Could not retrieve collections: {e}")
            continue

        if not collections:
            print("  No collections found.\n")
            continue

        print(f"  Found {len(collections)} collection(s).\n")

        for col in collections:
            flag, reason = should_delete(col)

            try:
                count = col.childCount
            except AttributeError:
                count = "?"

            if flag:
                total_flagged += 1
                status = "WOULD DELETE" if DRY_RUN else "DELETING"
                print(f"  [{status}] \"{col.title}\"  ({count} items)  → {reason}")
                if not DRY_RUN:
                    try:
                        col.delete()
                        total_deleted += 1
                    except Exception as e:
                        print(f"    ERROR deleting: {e}")
            else:
                total_kept += 1
                print(f"  [  KEEP   ] \"{col.title}\"  ({count} items)")

        print()

    # Summary
    print(f"{'='*60}")
    print(f"  Summary")
    print(f"  Collections flagged : {total_flagged}")
    if DRY_RUN:
        print(f"  Collections kept    : {total_kept}")
        print(f"\n  ✅ Dry run complete. No changes were made.")
        print(f"  To delete the flagged collections, set DRY_RUN = False and re-run.")
    else:
        print(f"  Collections deleted : {total_deleted}")
        print(f"  Collections kept    : {total_kept}")
        print(f"\n  ✅ Cleanup complete.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
