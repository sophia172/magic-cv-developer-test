// Copyright (c) 2024 Magic Tech Ltd

package fit.magic.cv.repcounter

import com.chaquo.python.Python
import fit.magic.cv.PoseLandmarkerHelper
import com.google.gson.Gson

class ExerciseRepCounterImpl : ExerciseRepCounter() {


    override fun setResults(resultBundle: PoseLandmarkerHelper.ResultBundle) {

        val jsonStr = Gson().toJson(resultBundle)
        val msg = magicDriver.callAttr("update", jsonStr).toString()
        val lungeWorker = magicDriver.getValue("lunge_worker")
        val count = lungeWorker.getValue("count").toInt()
        val progress = lungeWorker.getValue("progress").toFloat()
        val liveProgress = lungeWorker.getValue("live_progress").toString()
        if (progress > 0.99f) {
            incrementRepCount() // Code to execute when progress is 1
        }
        sendProgressUpdate(progress)
        sendFeedbackMessage(msg)
    }
}
