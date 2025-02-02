// Copyright (c) 2024 Magic Tech Ltd

package fit.magic.cv.repcounter

import com.chaquo.python.Python
import fit.magic.cv.PoseLandmarkerHelper
import com.google.gson.Gson

class ExerciseRepCounterImpl : ExerciseRepCounter() {


    override fun setResults(resultBundle: PoseLandmarkerHelper.ResultBundle) {
//        val python = Python.getInstance()
//        val pyModule = python.getModule("pycode")  // Name of your Python script without .py
//        val magicDriver = pyModule.callAttr("magic_driver", 24)  // Call the Python function

        val jsonStr = Gson().toJson(resultBundle)
        val result = magicDriver.callAttr("update", jsonStr)
        val lungeWorker = magicDriver.getValue("lunge_worker")
        val count = lungeWorker.getValue("count").toInt()
        val progress = lungeWorker.getValue("progress").toFloat()
        val liveProgress = lungeWorker.getValue("live_progress").toString()
        if ((kotlin.math.abs(progress - 1.0f) < 0.0001f)) {
            incrementRepCount() // Code to execute when progress is 1
        }
        sendProgressUpdate(progress)
        sendFeedbackMessage(liveProgress)
    }
}
