from typing import List, Tuple

import torch
import torchaudio
from torch import nn

from compxgan.modules import safe_log


class MelSpecReconstructionLoss(nn.Module):
    """
    L1 distance between the mel-scaled magnitude spectrograms of the ground truth sample and the generated sample
    """

    def __init__(
        self,
        sample_rate: int = 24000,
        n_fft: int = 1024,
        hop_length: int = 256,
        n_mels: int = 100,
    ):
        super().__init__()
        self.mel_spec = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            n_mels=n_mels,
            center=True,
            power=1,
        )

    def forward(self, y_hat, y) -> torch.Tensor:
        """
        Args:
            y_hat (Tensor): Predicted audio waveform.
            y (Tensor): Ground truth audio waveform.

        Returns:
            Tensor: L1 loss between the mel-scaled magnitude spectrograms.
        """
        mel_hat = safe_log(self.mel_spec(y_hat))
        mel = safe_log(self.mel_spec(y))

        loss = torch.nn.functional.l1_loss(mel, mel_hat)

        return loss


class GeneratorLoss(nn.Module):
    """
    Generator Loss module. Calculates the loss for the generator based on discriminator outputs.
    """

    def forward(
        self, disc_outputs: List[torch.Tensor]
    ) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """
        Args:
            disc_outputs (List[Tensor]): List of discriminator outputs.

        Returns:
            Tuple[Tensor, List[Tensor]]: Tuple containing the total loss and a list of loss values from
                                         the sub-discriminators
        """
        loss = torch.zeros(
            1, device=disc_outputs[0].device, dtype=disc_outputs[0].dtype
        )
        gen_losses = []
        for dg in disc_outputs:
            l = torch.mean(torch.clamp(1 - dg, min=0))
            gen_losses.append(l)
            loss += l

        return loss, gen_losses


class DiscriminatorLoss(nn.Module):
    """
    Discriminator Loss module. Calculates the loss for the discriminator based on real and generated outputs.
    """

    def forward(
        self,
        disc_real_outputs: List[torch.Tensor],
        disc_generated_outputs: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, List[torch.Tensor], List[torch.Tensor]]:
        """
        Args:
            disc_real_outputs (List[Tensor]): List of discriminator outputs for real samples.
            disc_generated_outputs (List[Tensor]): List of discriminator outputs for generated samples.

        Returns:
            Tuple[Tensor, List[Tensor], List[Tensor]]: A tuple containing the total loss, a list of loss values from
                                                       the sub-discriminators for real outputs, and a list of
                                                       loss values for generated outputs.
        """
        loss = torch.zeros(
            1, device=disc_real_outputs[0].device, dtype=disc_real_outputs[0].dtype
        )
        r_losses = []
        g_losses = []
        for dr, dg in zip(disc_real_outputs, disc_generated_outputs):
            r_loss = torch.mean(torch.clamp(1 - dr, min=0))
            g_loss = torch.mean(torch.clamp(1 + dg, min=0))
            loss += r_loss + g_loss
            r_losses.append(r_loss)
            g_losses.append(g_loss)

        return loss, r_losses, g_losses


class FeatureMatchingLoss(nn.Module):
    """
    Feature Matching Loss module. Calculates the feature matching loss between feature maps of the sub-discriminators.
    """

    def forward(
        self, fmap_r: List[List[torch.Tensor]], fmap_g: List[List[torch.Tensor]]
    ) -> torch.Tensor:
        """
        Args:
            fmap_r (List[List[Tensor]]): List of feature maps from real samples.
            fmap_g (List[List[Tensor]]): List of feature maps from generated samples.

        Returns:
            Tensor: The calculated feature matching loss.
        """
        loss = torch.zeros(1, device=fmap_r[0][0].device, dtype=fmap_r[0][0].dtype)
        for dr, dg in zip(fmap_r, fmap_g):
            for rl, gl in zip(dr, dg):
                loss += torch.mean(torch.abs(rl - gl))

        return loss


class cFeatureMatchingLoss(nn.Module):

    def forward(
        self, fmap_r: List[List[torch.Tensor]], fmap_g: List[List[torch.Tensor]]
    ) -> torch.Tensor:

        loss = torch.zeros(1, device=fmap_r[0][0].device)
        for dr, dg in zip(fmap_r, fmap_g):
            for rl, gl in zip(dr, dg):
                abs_loss = torch.mean(torch.abs(rl - gl)).float()
                phase_diff = torch.angle(rl) - torch.angle(gl)
                phase_loss = torch.mean(1 - torch.cos(phase_diff))
                loss += abs_loss + phase_loss

        return loss


class cGeneratorLoss(nn.Module):

    def forward(
        self, disc_outputs: List[torch.Tensor]
    ) -> Tuple[torch.Tensor, List[torch.Tensor]]:

        loss = torch.zeros(1, device=disc_outputs[0].device)
        gen_losses = []
        for dg in disc_outputs:

            l_abs = torch.mean(torch.clamp(torch.abs(1 - dg), min=0))
            phase = torch.angle(dg)
            l_phase = torch.mean(1 - torch.cos(phase))

            l = l_abs + l_phase
            gen_losses.append(l)
            loss += l

        return loss, gen_losses


class cDiscriminatorLoss(nn.Module):
    def forward(
        self,
        disc_real_outputs: List[torch.Tensor],
        disc_generated_outputs: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, List[torch.Tensor], List[torch.Tensor]]:

        loss = torch.zeros(1, device=disc_real_outputs[0].device)
        r_losses = []
        g_losses = []
        for dr, dg in zip(disc_real_outputs, disc_generated_outputs):
            r_abs_loss = torch.mean(torch.clamp(1 - torch.abs(dr), min=0))
            g_abs_loss = torch.mean(torch.clamp(torch.abs(dg), min=0))

            phase_r = torch.angle(dr)
            phase_f = torch.angle(dg)
            pr_loss = torch.mean(1 - torch.cos(phase_r))
            pf_loss = torch.mean(1 + torch.cos(phase_f))
            r_loss = r_abs_loss + pr_loss
            g_loss = g_abs_loss + pf_loss
            loss += r_loss + g_loss
            r_losses.append(r_loss)
            g_losses.append(g_loss)

        return loss, r_losses, g_losses
