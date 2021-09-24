#include "stdio.h"
unsigned long crc_table[256];
int crc_table_computed = 0;
typedef unsigned long DWORD;
void make_crc_table(void) {
  unsigned long c; int n, k;
  for (n = 0; n < 256; n++) {
    c = (unsigned long)n;
    for (k = 0; k < 8; k++) {
      if (c & 1) c = 0xedb88320L ^ (c >> 1);
      else c = c >> 1;
    } crc_table[n] = c;
  } crc_table_computed = 1;
}

unsigned long update_crc(unsigned long crc, unsigned char* buf, int len) {
  unsigned long c = crc; int n;
  if (!crc_table_computed) make_crc_table();
  for (n = 0; n < len; n++) {
    c = crc_table[(c ^ buf[n]) & 0xff] ^ (c >> 8);
  }
  return c;
}

/* Return the CRC of the bytes buf[0..len-1]. */
unsigned long crc(unsigned char* buf, int len) {
  return update_crc(0xffffffffL, buf, len) ^ 0xffffffffL;
}

int main() {
  unsigned char IHDR[] = "\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE";
  unsigned int w, h, i;
  unsigned int target_crc = 0x69696969;
  int max = 100000;
  for (w = 0; w < max; w++) {
    for (h = 0; h < max; h++) {
      *(DWORD*)&IHDR[4] = w;
      __asm__("bswap %0" : "+r" (*(DWORD*)&IHDR[4]));
      *(DWORD*)&IHDR[8] = h;
      __asm__("bswap %0" : "+r" (*(DWORD*)&IHDR[8]));
      //60 44 4c b6
      if (crc(IHDR, 17) == target_crc) {
        printf("W:%d H:%d\n", w, h);
        return 0;
      }
    }
  }
  return 1;
}