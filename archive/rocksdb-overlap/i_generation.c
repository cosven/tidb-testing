#include <stdint.h>
#include <sys/ioctl.h>
#include <sys/fcntl.h>
#include <sys/stat.h>
#include <linux/fs.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>

int main (int argc, char **argv) {
  if (argc < 2) {
      printf("Usage: %s <filename>\n", argv[0]);
      return 1;
  }

  const char *filename = argv[1];
  uint32_t generation = 666;
  struct stat file_stat;

  int fileno = open(filename, O_RDONLY);
  if (fileno < 0) {
      printf("Open file %s error", filename);
      return 1;
  }
  int ret = fstat(fileno, &file_stat);
  if (ret < 0) {
      printf("Stat file %s error", filename);
      return 1;
  }

  // get inode number and generation number
  if (ioctl(fileno, FS_IOC_GETVERSION, &generation)) {
      printf("Get generation number errno: %d\n", errno);
  }
  printf("inode number: %lu\n", file_stat.st_ino);
  printf("inode generation: %u\n", generation);

  close(fileno);

  return 0;
}
