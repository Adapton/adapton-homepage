initSidebarItems({"enum":[["AllocCase","Distinguish fresh allocations from those that reuse an existing location."],["AllocKind","Distinguish ref cell allocations from thunk allocations"],["Effect","The effects of the DCG (including cleaning and dirtying) on one of its edges."],["ForceCase","When the program `force`s a computation, either the cache is either empty (`CacheMiss`) or non-empty (`CacheHit`).  The cached value may not be consistent without a cleaning.  When the program `force`s a reference cell, it simply gets the current value."]],"struct":[["Edge","An edge in the DCG, representing an effect of the incremental program."],["Trace","`DCGTrace`: A Rose-tree of DCG edge-effects.  This tree structure allows the effects to have a a \"time interval\" that nests around and within the time intervals of other effects."]]});