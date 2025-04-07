package fit.magic.cv.repcounter

import fit.magic.cv.PoseLandmarkerHelper
import kotlin.math.*
import java.util.*

data class Quadruple<A, B, C, D>(
    val x: A,
    val y: B,
    val z: C,
    val vis: D
)
class MagicDriver(private val freq: Int) {
    private val body: Deque<Boolean> = ArrayDeque<Boolean>(freq)
    private var human: Boolean = false
    val lungeWorker = LungeWorker(frequency = 24, enableDtw = false, jointNum = 4)

    // Indices of joints you care about
    val jointIndices = listOf(11, 23, 25, 27, 12, 24, 26, 28)


    fun update(resultBundle: PoseLandmarkerHelper.ResultBundle): Float {
        val poseLandmarkerResult = resultBundle.results.firstOrNull()
        var jointCoordinates: List<Quadruple<Float, Float, Float, Float>> = emptyList()

        if (!poseLandmarkerResult?.landmarks().isNullOrEmpty()) {
            poseLandmarkerResult?.landmarks()?.forEachIndexed { poseIndex, landmarksList ->
                // Ensure the landmarks list is not empty before processing
                if (landmarksList.isNotEmpty()) {
                    // Assign values to new variables for each joint index in jointIndices
                    jointCoordinates = jointIndices.map { index ->
                        val landmark = landmarksList[index]
                        Quadruple(landmark.x(), landmark.y(), landmark.z(), landmark.visibility().orElse(0.0f))
                    }

                    val allVisible = jointCoordinates.all { it.vis > 0.5 }
                    body.addLast(allVisible)

                } else {body.addLast(false)}
            }
        } else {body.addLast(false)}

        if (body.size > freq) {body.removeFirst()}
        updateHumanStatus()
        if (human) {
            val angles = hipKneeAngle(jointCoordinates)
            lungeWorker.update(angles)
            return lungeWorker.liveProgress
        }
        return 0.0f

    }


    private fun updateHumanStatus() {
        human = if (!human) body.all { it } else !body.all { it }
    }
}
//

fun coordinatesToAngle(A: FloatArray, B: FloatArray): List<Int> {
    val R = rotationMatrix(A, B)
    val angles = decomposeRXYZ(R)
    val norm = sqrt(angles.map { it * it }.sum())
    return angles.map { it.toInt() } + norm.toInt()
}

fun decomposeRXYZ(R: Array<FloatArray>): FloatArray {
    val beta = -asin(R[2][0])
    val alpha: Float
    val gamma: Float

    if (abs(R[2][0]) < 1f) {
        alpha = atan2(R[1][0], R[0][0])
        gamma = atan2(R[2][1], R[2][2])
    } else {
        alpha = atan2(-R[0][1], R[1][1])
        gamma = 0f
    }

    return floatArrayOf(
        Math.toDegrees(gamma.toDouble()).toFloat(),
        Math.toDegrees(beta.toDouble()).toFloat(),
        Math.toDegrees(alpha.toDouble()).toFloat()
    )
}

fun rotationMatrix(A: FloatArray, B: FloatArray): Array<FloatArray> {
    val uA = normalize(A)
    val uB = normalize(B)

    val v = cross(uA, uB)
    val s = sqrt(dot(v, v))
    val c = dot(uA, uB)

    val vx = arrayOf(
        floatArrayOf(0f, -v[2], v[1]),
        floatArrayOf(v[2], 0f, -v[0]),
        floatArrayOf(-v[1], v[0], 0f)
    )

    val I = arrayOf(
        floatArrayOf(1f, 0f, 0f),
        floatArrayOf(0f, 1f, 0f),
        floatArrayOf(0f, 0f, 1f)
    )

    val vx2 = Array(3) { i ->
        FloatArray(3) { j ->
            (0..2).map { k -> vx[i][k] * vx[k][j] }.sum()
        }
    }

    val R = Array(3) { i -> FloatArray(3) { j ->
        I[i][j] + vx[i][j] + vx2[i][j] * ((1 - c) / (s * s))
    }}

    return R
}
fun subtract(a: FloatArray, b: FloatArray): FloatArray {
    return FloatArray(3) { i -> a[i] - b[i] }
}
fun hipKneeAngle(kpts: List<Quadruple<Float, Float, Float, Float>>): List<List<Int>> {
    val pts = kpts.map { floatArrayOf(it.x, it.y, it.z) }

    val segments = listOf(
        Pair(subtract(pts[1], pts[0]), subtract(pts[2], pts[1])),
        Pair(subtract(pts[2], pts[1]), subtract(pts[3], pts[2])),
        Pair(subtract(pts[5], pts[4]), subtract(pts[6], pts[5])),
        Pair(subtract(pts[6], pts[5]), subtract(pts[7], pts[6]))
    )

    return segments.map { (a, b) -> coordinatesToAngle(a, b) }
}

fun normalize(v: FloatArray): FloatArray {
    val norm = sqrt(v.map { it * it }.sum())
    return v.map { it / norm }.toFloatArray()
}

fun cross(a: FloatArray, b: FloatArray): FloatArray {
    return floatArrayOf(
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    )
}

fun dot(a: FloatArray, b: FloatArray): Float {
    return a.zip(b).map { it.first * it.second }.sum()
}

class LungeWorker(
    private val frequency: Int = 24,
    private val enableDtw: Boolean = false,
    private val jointNum: Int = 4
) {
    private val history: Deque<List<List<Float>>> = ArrayDeque(frequency)
    private val leg: Deque<Int> = ArrayDeque(frequency / 2)
    var progress: Float = 0f
    var count: Int = 0
    var liveProgress: Float = 0f
    var progressBar: Boolean = false
    private var min = floatArrayOf(360f, 360f)

    fun update(angles: List<List<Int>>): List<Int> {
        val anglesArray = maxAngle(angles.map { it.map { it.toFloat() }.toFloatArray() }.toTypedArray())
        // Map each FloatArray to List<Float> and add it to history
        history.addLast(anglesArray.map { it.toList() })
        updateProgress()
        return anglesArray.last().map { it.toInt() }
    }

    private fun maxAngle(angles: Array<FloatArray>): Array<FloatArray> {
        val leg = angles.indexOfFirst { it.last() == it.maxOrNull() } / 2
        return arrayOf(
            angles[leg * 2],
            angles[leg * 2 + 1],
            angles[2 - leg * 2],
            angles[3 - leg * 2]
        )
    }

    private fun _hipKnee(): Pair<Float, Float> {
        val windowSize = frequency / 4
        val hip = history.toList()
            .takeLast(windowSize)              // Take the last 'windowSize' elements
            .flatMap { it[0] }                 // Flatten the list of lists into a single list
            .average()                         // Compute the average of all the values
            .toFloat()
        val knee = history.toList()
            .takeLast(windowSize)              // Take the last 'windowSize' elements
            .flatMap { it[1] }                 // Flatten the list of lists into a single list
            .average()                         // Compute the average of all the values
            .toFloat()
        return hip to knee
    }

    private fun _progress(hip: Float, knee: Float): Float {
        min[0] = minOf(min[0], hip)  // Update the minimum for hip
        min[1] = minOf(min[1], knee) // Update the minimum for knee
        val hipProgress = ((hip - min[0]) / 25).coerceIn(0f, 1f)
        val kneeProgress = ((knee - min[1]) / 55).coerceIn(0f, 1f)
        println(hip to knee to kneeProgress to min[1])
        return kneeProgress
    }

    private fun updateProgress() {
        if (abs(progress - 1f) < 0.009f) {
            count++
            progress = 0f
            min.fill(360f)
            progressBar = false
        }
        val (hip, knee) = _hipKnee()
        liveProgress = _progress(hip, knee)
        if (abs(progress - 0f) < 0.01f && liveProgress >= 0.35f) {
            progressBar = true
        }
        if (progressBar && liveProgress > progress) {
            progress = liveProgress
        }
    }
}