import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global
import scala.util.{Failure, Success}


// TODO: take a look at https://github.com/lichess-org/lila/ to see how a big project's structured
// https://docs.scala-lang.org/scala3/book/concurrency.html
val startTime = System.currentTimeMillis()
def delta() = System.currentTimeMillis() - startTime
def sleep(millis: Long) = Thread.sleep(millis)

@main def multipleFutures1 =
    println(s"creating the futures:   ${delta()}")

    // (1) start the computations that return futures
    val f1 = Future { sleep(800); 1 }   // eventually returns 1
    val f2 = Future { sleep(200); 2 }   // eventually returns 2
    val f3 = Future { sleep(400); 3 }   // eventually returns 3

    // (2) join the futures in a `for` expression
    val result =
        for
            r1 <- f1
            r2 <- f2
            r3 <- f3
        yield
            println(s"in the 'yield': ${delta()}")
            (r1 + r2 + r3)

    // (3) process the result
    result.onComplete {
        case Success(x) =>
            println(s"in the Success case: ${delta()}")
            println(s"result = $x")
        case Failure(e) =>
            e.printStackTrace
    }

    println(s"before the 'sleep(3000)': ${delta()}")

    // important for a little parallel demo: keep the jvm alive
    sleep(3000)
