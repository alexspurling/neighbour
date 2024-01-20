;version 4
;debugflags trace

(defun format-time(sec &optional (n 3))
  ;; Return time formatted to hh:mm:ss + n decimal places.
  (unless (and (numberp sec) (numberp n))
    (error "format-time arguments must be numbers."))
  (flet ((pad (x) (if (< x 10) (format nil "0~a" x) x)))
    (let* ((hh (truncate (/ sec 3600)))
           (mm (truncate (/ sec 60)))
           (ss (- sec (* mm 60)))
           (old-format *float-format*)
           rslt)
      (setf mm (- mm (* hh 60)))
      (setf *float-format* (format nil "%.~af" n))
      (if (> hh 0)
          (setf rslt (format nil "~a:~a:~a" hh (pad mm) (pad ss)))
          (setf rslt (format nil "~a:~a" (pad mm) (pad ss)))
      )
      (setf *float-format* old-format)
      rslt)))

; get selection start in ms
(format t (format nil "(~s, ~s)," (format-time (get '*selection*' start) 0) (format-time (get '*selection*' end) 0)))

""