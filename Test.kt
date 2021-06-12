import java.util.*
import java.time.LocalDateTime
import java.time.Instant



fun main() {
    val timestamp = 1623526260L
    val instant = Instant.ofEpochSecond(timestamp, 0)
    print(instant.toString())
}
