# git-branch-tree

Executing tree.py from within a git repository will query all git branches and print them to the terminal in a hierarchical tree format, according to their upstream branch mapping.

### Default git branch terminal output
```
> git br -vv
  add_monitor_classes           eff3f10 [cleanup_for_separation: ahead 1] Create the ComparisonMonitor Class
  cleanup_for_separation        9981417 [master: ahead 3] Make optional the get_value_of_dcs_id return
  example_of_failing_tests      80bc338 [origin/example_of_failing_tests] Merge branch 'master' into example_of_failing_tests
  master                        db87ed9 [origin/master] Update build and test CI workflow
  newtest                       db87ed9 [master] Update build and test CI workflow
  reorganize_source_files       44276d7 [origin/reorganize_source_files] Move StreamdeckContext and Utilities to top level
* streamdeck_context_base_class d202fd2 [cleanup_for_separation: ahead 1, behind 1] Create context base class
```
  
### Script branch output
Executing `tree.py` shows:  

![Example printout with color formatting](printout_example.png)

