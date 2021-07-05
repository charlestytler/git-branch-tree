# git-branch-tree

Executing tree.py from within a git repository will query all git branches and print them to the terminal in a hierarchical tree format, according to their upstream branch mapping.

```
> git br -vv
  add_monitor_classes           eff3f10 [cleanup_for_separation: ahead 1] Create the ComparisonMonitor Class
  cleanup_for_separation        9981417 [master: ahead 3] Make optional the get_value_of_id return
  example_of_failing_tests      80bc338 [origin/example_of_failing_tests] Merge branch 'master' into example_of_failing_tests
  master                        db87ed9 [origin/master] Update build and test CI workflow
  newtest                       db87ed9 [master] Update build and test CI workflow
  reorganize_source_files       44276d7 [origin/reorganize_source_files] Move Context and Utilities to top level
* systemdeck_context_base_class d202fd2 [cleanup_for_separation: ahead 1, behind 1] Create context base class
```

Executing `tree.py` shows:
```
Branch                                Deltas    Commit  Description
=========================================================================
example_of_failing_tests              +0:-0     80bc338 Merge branch 'master' into example_of_failing_tests
master                                +0:-0     db87ed9 Update build and test CI workflow
 ├──cleanup_for_separation            +3:-0     9981417 Make optional the get_value_of_id return
 │  ├──add_monitor_classes            +1:-0     eff3f10 Create the ComparisonMonitor Class
 │  └──systemdeck_context_base_class  +1:-1     d202fd2 Create context base class
 └──newtest                           +0:-0     db87ed9 Update build and test CI workflow
reorganize_source_files               +0:-0     44276d7 Move Context and Utilities to top level
```

