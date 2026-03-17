import sounddevice as sd
import numpy as np
import scipy.signal as signal
import time
import soundfile as sf


def get_soundcard_outstream(device_list):
    for i, each in enumerate(device_list):
        dev_name = each["name"]
        asio_in_name = "ASIO Fireface" in dev_name
        if asio_in_name:
            return i


def pow_two_pad_and_window(vec, show=False):
    window = signal.windows.tukey(len(vec), alpha=0.2)
    windowed_vec = vec * window
    padded_windowed_vec = np.pad(
        windowed_vec,
        (0, 2 ** int(np.ceil(np.log2(len(windowed_vec)))) - len(windowed_vec)),
    )
    # if show:
    #     dur = len(padded_windowed_vec) / fs
    #     t = np.linspace(0, dur, len(windowed_vec))
    #     plt.figure()
    #     plt.subplot(2, 1, 1)
    #     plt.plot(t, windowed_vec)
    #     plt.subplot(2, 1, 2)
    #     plt.specgram(windowed_vec, NFFT=256, Fs=192e3)
    #     plt.show()
    return padded_windowed_vec / max(padded_windowed_vec)


def pow_two(vec):
    return np.pad(vec, (0, 2 ** int(np.ceil(np.log2(len(vec)))) - len(vec)))


if __name__ == "__main__":

    fs = 48000
    dur = 10e-3
    hi_freq = 4e3
    low_freq = 100
    n_sweeps = 500

    t_tone = np.linspace(0, dur, int(fs * dur))
    chirp = signal.chirp(t_tone, hi_freq, t_tone[-1], low_freq)
    sig = pow_two_pad_and_window(chirp, show=True)

    silence_dur = 500  # [ms]
    silence_samples = int(silence_dur * fs / 1000)
    silence_vec = np.zeros((silence_samples,))
    full_sig = pow_two(np.concatenate((sig, silence_vec)))

    # stereo_sig = np.hstack([full_sig.reshape(-1, 1), full_sig.reshape(-1, 1)])
    # output_sig = np.float32(stereo_sig)

    # 6 channel version
    multich_signal = np.float32(
        np.hstack(
            [
                full_sig.reshape(-1, 1),
                full_sig.reshape(-1, 1),
                full_sig.reshape(-1, 1),
                full_sig.reshape(-1, 1),
                full_sig.reshape(-1, 1),
                full_sig.reshape(-1, 1),
            ]
        )
    )
    print("multich", multich_signal.shape)
    output_sig = np.float32(np.tile(multich_signal, (500, 1)))

    sf.write("multich-500_chirp_11-4000_48khz.wav", 0.8 * output_sig, samplerate=fs)

    current_frame = 0

    def callback(outdata, frames, time, status):
        global current_frame
        if status:
            print(status)
        chunksize = min(len(output_sig) - current_frame, frames)
        outdata[:chunksize] = output_sig[current_frame : current_frame + chunksize]
        if chunksize < frames:
            outdata[chunksize:] = 0
            raise sd.CallbackAbort()
        current_frame += chunksize

    device = get_soundcard_outstream(sd.query_devices())

    try:
        for i in range(n_sweeps):
            stream = sd.OutputStream(
                samplerate=fs,
                blocksize=0,
                device=device,
                channels=6,
                callback=callback,
                latency="low",
            )

            with stream:
                while stream.active:
                    pass

            current_frame = 0
            print("Chirped %d" % (i + 1))
            # time.sleep(1)

    except KeyboardInterrupt:
        print("Interrupted by user")
