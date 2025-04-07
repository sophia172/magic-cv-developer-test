// Copyright (c) 2024 Magic Tech Ltd

package fit.magic.cv.repcounter

import com.chaquo.python.Python
import fit.magic.cv.PoseLandmarkerHelper

class ExerciseRepCounterImpl : ExerciseRepCounter() {


    override fun setResults(resultBundle: PoseLandmarkerHelper.ResultBundle) {


        val msg = magicDriver.update(resultBundle)
//        val count =  magicDriver.lungeWorker.count
        val progress = magicDriver.lungeWorker.progress
        val liveProgress = magicDriver.lungeWorker.liveProgress
        if (progress > 0.99f) {
            incrementRepCount() // Code to execute when progress is 1
        }
        sendProgressUpdate(progress)
        sendFeedbackMessage(msg.toString())
    }
}
