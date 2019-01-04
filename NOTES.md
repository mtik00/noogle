# Releasing

1.  modify the version:  `fab ver.rev`
1.  modify `release-notes.md`
1.  git push/merge/etc the release notes
1.  Create a tag:  
    `fab git.create_tag`
1.  Build/copy the files:
    `fab release`
