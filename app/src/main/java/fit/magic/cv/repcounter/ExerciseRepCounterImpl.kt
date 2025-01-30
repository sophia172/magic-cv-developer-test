// Copyright (c) 2024 Magic Tech Ltd

package fit.magic.cv.repcounter

import com.chaquo.python.Python
import fit.magic.cv.PoseLandmarkerHelper

class ExerciseRepCounterImpl : ExerciseRepCounter() {

    override fun setResults(resultBundle: PoseLandmarkerHelper.ResultBundle) {
        val python = Python.getInstance()
        val pyObject = python.getModule("pycode")  // Name of your Python script without .py
        val result = pyObject.callAttr("confidence", resultBundle)  // Call the Python function
        incrementRepCount()
        val currentReps = 0.1f
        sendProgressUpdate(currentReps)
        sendFeedbackMessage(result.toString())
    }
}
