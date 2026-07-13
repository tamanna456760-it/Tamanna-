# Create a bare mirror (offline)
git clone --mirror /path/to/bd_king_r7 /path/to/backup_root/r7_repo_mirror.git

# Verify
cd /path/to/backup_root/r7_repo_mirror.git
git fsck

# Restore working copy later
git clone /path/to/backup_root/r7_repo_mirror.git /path/to/restore/bd_king_r7
