# CompXGAN: Complex-Valued Neural Vocoder With iSTFT-Based Waveform Generation

Anonymous

## Abstract

Recent advances in neural vocoders have significantly improved speech synthesis quality through generative models. Among these, inverse short-time Fourier transform (iSTFT)-based approaches have gained attention for directly generating waveforms in the spectral domain without upsampling. However, most iSTFT-based vocoders rely on real-valued networks that treat real and imaginary parts independently, limiting their ability to capture complex spectrogram structure. We present CompXGAN, a vocoder that adopts complex-valued neural networks (CVNNs) in both the generator and discriminator to better model spectral correlations in the complex domain. The generator jointly processes real and imaginary components, while the complex multi-resolution discriminator (cMRD) provides consistent spectral feedback using complex-valued inputs. To support structured transformation in the phase domain, we introduce phase quantization, which discretizes phase values and regularizes learning. We also propose a block-matrix computation scheme that improves training efficiency by reducing redundant graph operations. Experiments demonstrate that CompXGAN outperforms real-valued baselines in synthesis quality. Moreover, its block-matrix computation scheme reduces training time by 34%. Audio samples and code are available at https://anonymous7136.github.io/.

## Train
```
python train.py -c configs/compxgan.yaml
```

## Inference 
```
python infer.py -c configs/compxgan.yaml --file_list=test.txt
```
