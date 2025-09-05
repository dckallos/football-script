// Async example with parallel gather
async def main() {
  results = parallel{ sleep_ms(50), sleep_ms(20) };
  print("done");
}
main()
