from typing import Final

from model.instrument import Instrument

ALL_INSTRUMENTS: Final[tuple] = (
    Instrument(1, "StagePno", 0, 1),
    Instrument(2, "GrandPno", 0, 3),
    Instrument(3, "BrtPiano", 1, 1),
    Instrument(4, "MlwPiano", 0, 2),
    Instrument(5, "AmbPiano", 0, 39),
    Instrument(6, "PopPiano", 0, 32),
    Instrument(7, "Rock Pno", 1, 2),
    Instrument(8, "DancePno", 1, 3),
    Instrument(9, "LA Piano", 1, 4),
    Instrument(10, "Tack Pno", 0, 33),
    Instrument(11, "Mono Pno", 0, 4),
    Instrument(12, "HnkyTnk1", 3, 32),
    Instrument(13, "HnkyTnk2", 3, 34),
    Instrument(14, "Oct.Pno1", 3, 33),
    Instrument(15, "Oct.Pno2", 3, 35),
    Instrument(16, "GrndPnoW", 0, 5),
    Instrument(17, "StrPiano", 0, 34),
    Instrument(18, "PianoPad", 0, 35),
    Instrument(19, "ModPiano", 0, 36),
    Instrument(20, "VoicePno", 0, 37),
    Instrument(21, "NewAgePn", 0, 38),
    Instrument(22, "AmpEGrnd", 2, 34),
    Instrument(23, "E.Grand", 2, 32),
    Instrument(24, "MdernEGP", 2, 33),
    Instrument(25, "Harpsi.1", 6, 1),
    Instrument(26, "Harpsi.2", 6, 32),
    Instrument(27, "CouplHps", 6, 33),
    Instrument(28, "AmbHarps", 6, 35),
    Instrument(29, "GlaxiaEP", 5, 32),
    Instrument(30, "DynamcEP", 4, 32),
    Instrument(31, "LucentEP", 5, 33),
    Instrument(32, "E.Piano1", 4, 1),
    Instrument(33, "E.Piano2", 4, 2),
    Instrument(34, "E.Piano3", 4, 3),
    Instrument(35, "E.Piano4", 4, 4),
    Instrument(36, "E.Piano5", 5, 34),
    Instrument(37, "E.Piano6", 4, 5),
    Instrument(38, "Amp60sEP", 4, 35),
    Instrument(39, "60's EP", 4, 6),
    Instrument(40, "Amp EP1", 4, 36),
    Instrument(41, "Amp EP2", 4, 37),
    Instrument(42, "Dyno EP", 4, 33),
    Instrument(43, "Digi.EP1", 5, 1),
    Instrument(44, "Digi.EP2", 5, 2),
    Instrument(45, "Digi.EP3", 5, 3),
    Instrument(46, "PhaserEP", 4, 7),
    Instrument(47, "EP Wide", 4, 8),
    Instrument(48, "MellowEP", 4, 9),
    Instrument(49, "Wah EP", 4, 38),
    Instrument(50, "CrunchEP", 4, 39),
    Instrument(51, "Dizzy EP", 4, 40),
    Instrument(52, "EP Pad", 4, 34),
    Instrument(53, "AmpClavi", 7, 34),
    Instrument(54, "Clavi 1", 7, 1),
    Instrument(55, "Clavi 2", 7, 32),
    Instrument(56, "Clavi 3", 7, 2),
    Instrument(57, "Clavi 4", 7, 33),
    Instrument(58, "Clavi 5", 7, 3),
    Instrument(59, "Amb Vib.", 11, 32),
    Instrument(60, "Vibes 1", 11, 1),
    Instrument(61, "Vibes 2", 11, 2),
    Instrument(62, "Vib Wide", 11, 3),
    Instrument(63, "Marimba", 12, 32),
    Instrument(64, "Xylophon", 13, 1),
    Instrument(65, "Celesta", 8, 1),
    Instrument(66, "Glocken.", 9, 1),
    Instrument(67, "MusicBox", 10, 32),
    Instrument(68, "Orgel", 10, 33),
    Instrument(69, "Tubulbel", 14, 32),
    Instrument(70, "ChrchBel", 14, 33),
    Instrument(71, "JS Organ", 17, 32),
    Instrument(72, "RtfFdOrg", 16, 32),
    Instrument(73, "RokOdOrg", 18, 32),
    Instrument(74, "Trem.Org", 16, 5),
    Instrument(75, "DP Organ", 16, 4),
    Instrument(76, "JazzOrg1", 17, 33),
    Instrument(77, "JazzOrg2", 17, 34),
    Instrument(78, "ElecOrg1", 16, 1),
    Instrument(79, "ElecOrg2", 16, 2),
    Instrument(80, "ElecOrg3", 16, 33),
    Instrument(81, "ElecOrg4", 16, 34),
    Instrument(82, "ElecOrg5", 16, 35),
    Instrument(83, "PercOrg1", 17, 1),
    Instrument(84, "PercOrg2", 17, 35),
    Instrument(85, "GosplOrg", 17, 38),
    Instrument(86, "FullDrwb", 16, 3),
    Instrument(87, "RockOrg1", 18, 1),
    Instrument(88, "RockOrg2", 18, 2),
    Instrument(89, "ClickOrg", 17, 37),
    Instrument(90, "70's Org", 17, 36),
    Instrument(91, "OrganPad", 16, 6),
    Instrument(92, "PipeOrg1", 19, 32),
    Instrument(93, "PipeOrg2", 19, 33),
    Instrument(94, "PipeOrg3", 19, 2),
    Instrument(95, "ChaplOrg", 19, 34),
    Instrument(96, "Theater", 19, 1),
    Instrument(97, "PercOrg3", 17, 39),
    Instrument(98, "ElecOrg6", 16, 36),
    Instrument(99, "Amp Org1", 16, 37),
    Instrument(100, "Amp Org2", 16, 38),
    Instrument(101, "OrgFlute", 19, 35),
    Instrument(102, "Puff Org", 20, 33),
    Instrument(103, "AcrdFrc1", 21, 32),
    Instrument(104, "AcrdFrc2", 21, 33),
    Instrument(105, "AcrdFrc3", 21, 34),
    Instrument(106, "AcrdItl1", 21, 1),
    Instrument(107, "AcrdItl2", 21, 35),
    Instrument(108, "Acordion", 21, 2),
    Instrument(109, "Bandneon", 23, 32),
    Instrument(110, "Bdn Solo", 23, 1),
    Instrument(111, "Hrmonca1", 22, 32),
    Instrument(112, "Hrmonca2", 22, 33),
    Instrument(113, "NylonGtV", 24, 32),
    Instrument(114, "SteelGtV", 25, 32),
    Instrument(115, "NylonGt1", 24, 1),
    Instrument(116, "NylonGt2", 24, 2),
    Instrument(117, "NylonGt3", 24, 4),
    Instrument(118, "SteelGt1", 25, 1),
    Instrument(119, "SteelGt2", 25, 2),
    Instrument(120, "SteelGt3", 25, 3),
    Instrument(121, "SteelGt4", 25, 4),
    Instrument(122, "12Str.Gt", 25, 5),
    Instrument(123, "Jazz Gt1", 26, 1),
    Instrument(124, "Jazz Gt2", 26, 32),
    Instrument(125, "OdOtJzGt", 26, 2),
    Instrument(126, "CruJazGt", 26, 3),
    Instrument(127, "CleanGt1", 27, 32),
    Instrument(128, "CleanGt2", 27, 1),
    Instrument(129, "CleanGt3", 27, 2),
    Instrument(130, "CleanGt4", 27, 3),
    Instrument(131, "CleanGt5", 27, 4),
    Instrument(132, "CleanGt6", 27, 33),
    Instrument(133, "CleanGt7", 27, 7),
    Instrument(134, "ChoClGt1", 27, 5),
    Instrument(135, "ChoClGt2", 27, 6),
    Instrument(136, "WahClnGt", 27, 34),
    Instrument(137, "CrnchGt1", 29, 3),
    Instrument(138, "CrnchGt2", 29, 32),
    Instrument(139, "CrnchGt3", 27, 8),
    Instrument(140, "ChoCruGt", 29, 4),
    Instrument(141, "Mute Gt", 28, 1),
    Instrument(142, "CruMtGt", 28, 2),
    Instrument(143, "OvdMtGt", 28, 5),
    Instrument(144, "PhaMtGt", 28, 3),
    Instrument(145, "AmbMtGt", 28, 4),
    Instrument(146, "HumBlsGt", 29, 5),
    Instrument(147, "OvDrvGt1", 29, 1),
    Instrument(148, "OvDrvGt2", 29, 2),
    Instrument(149, "LWahOdGt", 29, 6),
    Instrument(150, "WahOD Gt", 29, 33),
    Instrument(151, "CryOD Gt", 29, 34),
    Instrument(152, "FlgOD Gt", 29, 35),
    Instrument(153, "Dist.Gt1", 30, 1),
    Instrument(154, "Dist.Gt2", 30, 2),
    Instrument(155, "Dist.Gt3", 30, 3),
    Instrument(156, "Dist.Gt4", 30, 5),
    Instrument(157, "WahDstGt", 30, 4),
    Instrument(158, "PhaDrvGt", 29, 36),
    Instrument(159, "VintOdGt", 29, 37),
    Instrument(160, "Amp Gt 1", 30, 35),
    Instrument(161, "Amp Gt 2", 30, 36),
    Instrument(162, "MtlAmbGt", 30, 32),
    Instrument(163, "FrtDrvGt", 30, 33),
    Instrument(164, "UpOctGt", 27, 35),
    Instrument(165, "C+R CrGt", 29, 40),
    Instrument(166, "OctMtlGt", 30, 34),
    Instrument(167, "Mandolin", 25, 40),
    Instrument(168, "Ukulele", 24, 3),
    Instrument(169, "VstNylGt", 24, 8),
    Instrument(170, "VstStlGt", 25, 8),
    Instrument(171, "VstSgEGt", 27, 9),
    Instrument(172, "AcousBs1", 32, 1),
    Instrument(173, "FingrBs1", 33, 6),
    Instrument(174, "FingrBs2", 33, 5),
    Instrument(175, "FgBV.Sl1", 33, 33),
    Instrument(176, "FgBV.Sl2", 33, 32),
    Instrument(177, "SlapBs 1", 36, 1),
    Instrument(178, "FgrSlpB1", 36, 5),
    Instrument(179, "ChoF.Bs1", 33, 39),
    Instrument(180, "PhazF.Bs", 33, 40),
    Instrument(181, "AmpF.Bs", 33, 38),
    Instrument(182, "WahF.Bs1", 33, 36),
    Instrument(183, "WahSlap1", 36, 36),
    Instrument(184, "SynBs 1", 39, 3),
    Instrument(185, "AcousBs2", 32, 32),
    Instrument(186, "RideBass", 32, 33),
    Instrument(187, "FingrBs3", 33, 1),
    Instrument(188, "FingrBs4", 33, 2),
    Instrument(189, "FingrBs5", 33, 3),
    Instrument(190, "FingrBs6", 33, 4),
    Instrument(191, "FingrBs7", 33, 7),
    Instrument(192, "ChoF.Bs2", 33, 8),
    Instrument(193, "WahF.Bs2", 33, 9),
    Instrument(194, "PickBs 1", 34, 1),
    Instrument(195, "PickBs 2", 34, 2),
    Instrument(196, "MutPicBs", 34, 5),
    Instrument(197, "SlapBs 2", 36, 32),
    Instrument(198, "SlapBs 3", 36, 2),
    Instrument(199, "ChoSlpBs", 36, 33),
    Instrument(200, "AmpSlpBs", 36, 3),
    Instrument(201, "WahSlap2", 36, 34),
    Instrument(202, "Fretless", 35, 32),
    Instrument(203, "ChoFrlBs", 35, 33),
    Instrument(204, "AmpFrlBs", 35, 34),
    Instrument(205, "FgrSlpB2", 36, 4),
    Instrument(206, "FgrSlpB3", 36, 35),
    Instrument(207, "SynBs 2", 38, 6),
    Instrument(208, "SynBs 3", 38, 1),
    Instrument(209, "SynBs 4", 38, 2),
    Instrument(210, "SynBs 5", 39, 1),
    Instrument(211, "SynBs 6", 39, 2),
    Instrument(212, "SynBs 7", 38, 32),
    Instrument(213, "SynBs 8", 39, 33),
    Instrument(214, "SynBs 9", 39, 4),
    Instrument(215, "SynBs 10", 39, 5),
    Instrument(216, "SynBs 11", 38, 4),
    Instrument(217, "SynBs 12", 38, 5),
    Instrument(218, "SynBs 13", 39, 6),
    Instrument(219, "Org Bass", 39, 7),
    Instrument(220, "VstE.Bs1", 33, 10),
    Instrument(221, "VstE.Bs2", 33, 24),
    Instrument(222, "StreoStr", 48, 32),
    Instrument(223, "MelwStr1", 49, 1),
    Instrument(224, "MelwStr2", 48, 1),
    Instrument(225, "BrtStr.1", 49, 2),
    Instrument(226, "BrtStr.2", 48, 38),
    Instrument(227, "Strings", 48, 3),
    Instrument(228, "SlwStStr", 49, 37),
    Instrument(229, "SlowStr1", 48, 2),
    Instrument(230, "SlowStr2", 49, 32),
    Instrument(231, "Str.Ens", 48, 4),
    Instrument(232, "WarmStrg", 48, 5),
    Instrument(233, "Pizz.Str", 45, 32),
    Instrument(234, "Chamber", 48, 33),
    Instrument(235, "Oct.Str.", 48, 34),
    Instrument(236, "OrchHit1", 55, 4),
    Instrument(237, "OrchHit2", 55, 32),
    Instrument(238, "OrchHit3", 55, 33),
    Instrument(239, "Brs&Str.", 48, 36),
    Instrument(240, "SolVioln", 40, 32),
    Instrument(241, "Violin", 40, 33),
    Instrument(242, "SlwVioln", 40, 34),
    Instrument(243, "Viola", 41, 32),
    Instrument(244, "Cello", 42, 32),
    Instrument(245, "SlwCello", 42, 33),
    Instrument(246, "Contrabs", 43, 32),
    Instrument(247, "Harp 1", 46, 32),
    Instrument(248, "Harp 2", 46, 34),
    Instrument(249, "ViolnSct", 48, 6),
    Instrument(250, "Str.Qrt.", 48, 37),
    Instrument(251, "Harp&Str", 49, 3),
    Instrument(252, "St.Brass", 61, 1),
    Instrument(253, "SolTrmpt", 56, 1),
    Instrument(254, "Syn-Brs1", 62, 32),
    Instrument(255, "Brass", 61, 2),
    Instrument(256, "BrsSect1", 61, 3),
    Instrument(257, "BrsSect2", 61, 4),
    Instrument(258, "BrsSect3", 61, 37),
    Instrument(259, "AmbBrass", 61, 38),
    Instrument(260, "BgBndBrs", 61, 32),
    Instrument(261, "HrdBrass", 61, 5),
    Instrument(262, "BrassSfz", 61, 33),
    Instrument(263, "BrasFall", 61, 34),
    Instrument(264, "BrasShak", 61, 35),
    Instrument(265, "BrasGlis", 61, 36),
    Instrument(266, "Syn-Brs2", 62, 33),
    Instrument(267, "Syn-Brs3", 62, 1),
    Instrument(268, "Syn-Brs4", 62, 34),
    Instrument(269, "Syn-Brs5", 62, 37),
    Instrument(270, "WrmSyBr1", 62, 35),
    Instrument(271, "WrmSyBr2", 62, 38),
    Instrument(272, "AnSynBrs", 62, 36),
    Instrument(273, "80sSyBrs", 62, 2),
    Instrument(274, "TrnceBrs", 63, 32),
    Instrument(275, "Trumpet1", 56, 32),
    Instrument(276, "Trumpet2", 56, 2),
    Instrument(277, "Trumpet3", 56, 36),
    Instrument(278, "MelowTrp", 56, 3),
    Instrument(279, "Mute Trp", 59, 1),
    Instrument(280, "Amb Trp", 56, 33),
    Instrument(281, "Trombone", 57, 32),
    Instrument(282, "Jazz Trb", 57, 33),
    Instrument(283, "Fr.Horn", 60, 32),
    Instrument(284, "FHornSct", 60, 1),
    Instrument(285, "Tuba", 58, 32),
    Instrument(286, "TrpTrbSx", 61, 39),
    Instrument(287, "VstBras1", 61, 8),
    Instrument(288, "VstBras2", 61, 9),
    Instrument(289, "SoloTSax", 66, 1),
    Instrument(290, "SoloASax", 65, 32),
    Instrument(291, "Vel.ASax", 65, 36),
    Instrument(292, "BrtyASax", 65, 33),
    Instrument(293, "SoloSSax", 64, 32),
    Instrument(294, "Vel.SSax", 64, 35),
    Instrument(295, "BrtySSax", 64, 34),
    Instrument(296, "ASaxGrwl", 65, 37),
    Instrument(297, "SoloOboe", 68, 32),
    Instrument(298, "SolBason", 70, 32),
    Instrument(299, "AltoSax1", 65, 39),
    Instrument(300, "AltoSax2", 65, 1),
    Instrument(301, "TenorSax", 66, 2),
    Instrument(302, "BrtyTSax", 66, 3),
    Instrument(303, "SoprSax1", 64, 36),
    Instrument(304, "SoprSax2", 64, 33),
    Instrument(305, "Bari.Sax", 67, 1),
    Instrument(306, "AmbSax1", 65, 38),
    Instrument(307, "AmbSax2", 67, 33),
    Instrument(308, "HardASax", 65, 2),
    Instrument(309, "T.Saxys", 66, 4),
    Instrument(310, "SaxSect1", 65, 40),
    Instrument(311, "SaxSect2", 65, 41),
    Instrument(312, "Clarinet", 71, 32),
    Instrument(313, "VelClari", 71, 1),
    Instrument(314, "Oboe", 68, 1),
    Instrument(315, "Eng.Horn", 69, 32),
    Instrument(316, "Bassoon", 70, 33),
    Instrument(317, "SolFlut1", 73, 32),
    Instrument(318, "SolFlut2", 73, 33),
    Instrument(319, "Flute 1", 73, 1),
    Instrument(320, "Flute 2", 73, 36),
    Instrument(321, "JzFlute1", 73, 2),
    Instrument(322, "JzFlute2", 73, 37),
    Instrument(323, "Piccolo", 72, 32),
    Instrument(324, "Recorder", 74, 32),
    Instrument(325, "PanFlut1", 75, 32),
    Instrument(326, "PanFlut2", 75, 33),
    Instrument(327, "BtleBlow", 76, 32),
    Instrument(328, "Whistle", 78, 1),
    Instrument(329, "Ocarina", 79, 32),
    Instrument(330, "Shakhchi", 77, 32),
    Instrument(331, "PipeSect", 72, 33),
    Instrument(332, "Flt&Oboe", 73, 38),
    Instrument(333, "SprSwLd1", 81, 16),
    Instrument(334, "SprSwLd2", 81, 17),
    Instrument(335, "TrncPoLd", 81, 18),
    Instrument(336, "TrncPlk", 81, 38),
    Instrument(337, "PrgrPlk", 81, 39),
    Instrument(338, "SawPlk", 81, 40),
    Instrument(339, "DirtyPlk", 80, 38),
    Instrument(340, "PopLead", 81, 43),
    Instrument(341, "HouseSyn", 81, 44),
    Instrument(342, "PopPlk1", 81, 19),
    Instrument(343, "PopPlk2", 81, 20),
    Instrument(344, "VcChSyn1", 85, 16),
    Instrument(345, "VcChSyn2", 85, 17),
    Instrument(346, "DModSyn1", 81, 45),
    Instrument(347, "DModSyn2", 81, 46),
    Instrument(348, "DModSyn3", 81, 47),
    Instrument(349, "X-SynLd1", 81, 7),
    Instrument(350, "X-SynLd2", 80, 36),
    Instrument(351, "X-SynLd3", 81, 32),
    Instrument(352, "X-SynLd4", 80, 37),
    Instrument(353, "X-SynLd5", 81, 33),
    Instrument(354, "X-SynLd6", 80, 6),
    Instrument(355, "VASynth1", 80, 3),
    Instrument(356, "VASynth2", 80, 4),
    Instrument(357, "VASynth3", 80, 5),
    Instrument(358, "VASeqBs1", 81, 10),
    Instrument(359, "VASeqBs2", 81, 11),
    Instrument(360, "VASeqBs3", 81, 12),
    Instrument(361, "VASynSq1", 81, 13),
    Instrument(362, "VASynSq2", 81, 14),
    Instrument(363, "Edm K&B", 96, 8),
    Instrument(364, "EdmLdSyn", 96, 36),
    Instrument(365, "EdmPerSy", 97, 10),
    Instrument(366, "Edm Lzr1", 96, 9),
    Instrument(367, "Edm Lzr2", 96, 10),
    Instrument(368, "EdmTmSy1", 96, 11),
    Instrument(369, "EdmTmSy2", 96, 34),
    Instrument(370, "EdmThmHt", 97, 8),
    Instrument(371, "EdmBrsHt", 96, 12),
    Instrument(372, "EdmBass", 97, 9),
    Instrument(373, "EdmSEBnd", 96, 13),
    Instrument(374, "EdmSEVox", 96, 14),
    Instrument(375, "EdmSEWht", 96, 15),
    Instrument(376, "EdmSE", 96, 35),
    Instrument(377, "SawLead1", 81, 1),
    Instrument(378, "SawLead2", 81, 2),
    Instrument(379, "SawLead3", 81, 3),
    Instrument(380, "MlwSawLd", 81, 4),
    Instrument(381, "PlsSawLd", 81, 5),
    Instrument(382, "TranceLd", 81, 6),
    Instrument(383, "SS Lead", 81, 34),
    Instrument(384, "SqrLead1", 80, 32),
    Instrument(385, "SqrLead2", 80, 41),
    Instrument(386, "SlwSqrLd", 80, 1),
    Instrument(387, "PhazSqLd", 80, 42),
    Instrument(388, "PulseLd1", 80, 33),
    Instrument(389, "PulseLd2", 80, 43),
    Instrument(390, "SqrPlsLd", 80, 34),
    Instrument(391, "SineLead", 80, 2),
    Instrument(392, "VelSinLd", 80, 44),
    Instrument(393, "SynSeqnc", 80, 8),
    Instrument(394, "Seq.Saw", 81, 15),
    Instrument(395, "Seq.Sine", 80, 7),
    Instrument(396, "8bitArp1", 80, 9),
    Instrument(397, "8bitArp2", 80, 45),
    Instrument(398, "8bitWave", 80, 35),
    Instrument(399, "SawArpg1", 81, 8),
    Instrument(400, "SawArpg2", 81, 9),
    Instrument(401, "D.ModLd1", 81, 48),
    Instrument(402, "D.ModLd2", 81, 49),
    Instrument(403, "D.ModLd3", 81, 50),
    Instrument(404, "VentLead", 82, 32),
    Instrument(405, "ChurchLd", 85, 32),
    Instrument(406, "DblVoiLd", 85, 34),
    Instrument(407, "SynVoiLd", 85, 1),
    Instrument(408, "Fifth Ld", 86, 32),
    Instrument(409, "FifthSaw", 86, 33),
    Instrument(410, "FifthSqr", 86, 34),
    Instrument(411, "4th Lead", 86, 35),
    Instrument(412, "7th Seq.", 86, 36),
    Instrument(413, "Bs+Lead", 87, 32),
    Instrument(414, "SynBs+Ld", 87, 33),
    Instrument(415, "ReedLead", 87, 34),
    Instrument(416, "GFunkLd", 81, 41),
    Instrument(417, "HopLead", 80, 39),
    Instrument(418, "HipLead", 80, 40),
    Instrument(419, "WireLead", 81, 35),
    Instrument(420, "FireWire", 81, 36),
    Instrument(421, "Syn-Str1", 51, 32),
    Instrument(422, "DgSyStr1", 51, 33),
    Instrument(423, "PrgrVoi", 88, 4),
    Instrument(424, "SprSawPd", 90, 6),
    Instrument(425, "OldTpPd", 88, 5),
    Instrument(426, "Fantasia", 88, 33),
    Instrument(427, "XenonPad", 88, 32),
    Instrument(428, "HousePad", 97, 33),
    Instrument(429, "D.ModPd1", 90, 36),
    Instrument(430, "D.ModPd2", 90, 37),
    Instrument(431, "D.ModPd3", 90, 38),
    Instrument(432, "X-SynPd1", 90, 32),
    Instrument(433, "X-SynPd2", 90, 33),
    Instrument(434, "X-SynPd3", 90, 34),
    Instrument(435, "Syn-Str2", 50, 1),
    Instrument(436, "Syn-Str3", 50, 2),
    Instrument(437, "70sSySt1", 50, 3),
    Instrument(438, "70sSySt2", 50, 32),
    Instrument(439, "80sSySt1", 50, 33),
    Instrument(440, "80sSySt2", 50, 34),
    Instrument(441, "DgSyStr2", 50, 4),
    Instrument(442, "FstSyStr", 50, 5),
    Instrument(443, "SlwSyStr", 50, 35),
    Instrument(444, "OctSyStr", 51, 35),
    Instrument(445, "Fantasy", 88, 1),
    Instrument(446, "New Age", 88, 2),
    Instrument(447, "Warm Pad", 89, 1),
    Instrument(448, "FatSawPd", 89, 2),
    Instrument(449, "Soft Pad", 89, 3),
    Instrument(450, "Poly Pad", 90, 35),
    Instrument(451, "Syn-Pad", 90, 1),
    Instrument(452, "VASynPad", 90, 2),
    Instrument(453, "Poly Saw", 90, 3),
    Instrument(454, "BrSawPd1", 90, 4),
    Instrument(455, "BrSawPd2", 90, 5),
    Instrument(456, "GlassPad", 92, 32),
    Instrument(457, "BotlePad", 92, 33),
    Instrument(458, "EthnicPd", 93, 32),
    Instrument(459, "SweepPad", 95, 1),
    Instrument(460, "WoodPad", 96, 32),
    Instrument(461, "SoundTrk", 97, 1),
    Instrument(462, "VibeBell", 98, 32),
    Instrument(463, "AtmosPad", 99, 1),
    Instrument(464, "SteelPad", 99, 32),
    Instrument(465, "Britness", 100, 1),
    Instrument(466, "BrtBelPd", 100, 2),
    Instrument(467, "SpacePad", 103, 1),
    Instrument(468, "Edm Pad", 88, 3),
    Instrument(469, "D.ModVo1", 52, 34),
    Instrument(470, "D.ModVo2", 52, 35),
    Instrument(471, "D.ModVo3", 52, 37),
    Instrument(472, "ChoirAah", 52, 1),
    Instrument(473, "StrVoi", 52, 33),
    Instrument(474, "SlwChor", 52, 32),
    Instrument(475, "VoiceDoo", 53, 32),
    Instrument(476, "VoiceUuh", 53, 33),
    Instrument(477, "SynVoi1", 54, 1),
    Instrument(478, "SynVoi2", 52, 36),
    Instrument(479, "VoiceEns", 54, 2),
    Instrument(480, "SynVoiPd", 54, 32),
    Instrument(481, "Warm Vox", 89, 32),
    Instrument(482, "SpaceCho", 91, 32),
    Instrument(483, "StarVoi", 91, 33),
    Instrument(484, "EchoVoi", 102, 32),
    Instrument(485, "Sitar 1", 104, 32),
    Instrument(486, "Sitar 2", 104, 1),
    Instrument(487, "Sitar 3", 104, 33),
    Instrument(488, "SitarPad", 104, 34),
    Instrument(489, "Tanpura1", 104, 2),
    Instrument(490, "Tanpura2", 104, 35),
    Instrument(491, "Hrmnium1", 20, 32),
    Instrument(492, "Hrmnium2", 20, 1),
    Instrument(493, "Santur 1", 15, 1),
    Instrument(494, "Santur 2", 15, 32),
    Instrument(495, "Sarod 1", 105, 10),
    Instrument(496, "Sarod 2", 105, 41),
    Instrument(497, "Sarangi1", 110, 8),
    Instrument(498, "Sarangi2", 110, 43),
    Instrument(499, "Veena 1", 104, 36),
    Instrument(500, "Veena 2", 104, 37),
    Instrument(501, "Shanai", 111, 1),
    Instrument(502, "Bansuri", 72, 9),
    Instrument(503, "Pungi", 111, 8),
    Instrument(504, "Tabla", 116, 41),
    Instrument(505, "AngklnTr", 12, 40),
    Instrument(506, "Gender", 11, 40),
    Instrument(507, "Cak", 25, 12),
    Instrument(508, "Cuk", 24, 40),
    Instrument(509, "CeloFing", 32, 12),
    Instrument(510, "Sasando", 46, 40),
    Instrument(511, "ShtSulng", 77, 40),
    Instrument(512, "SlngBmb1", 77, 41),
    Instrument(513, "Saluang", 77, 43),
    Instrument(514, "SlngBmb2", 77, 42),
    Instrument(515, "Oud 1", 105, 11),
    Instrument(516, "Oud 2", 105, 42),
    Instrument(517, "Saz", 15, 4),
    Instrument(518, "Kanun 1", 15, 5),
    Instrument(519, "Kanun 2", 15, 33),
    Instrument(520, "Bouzouki", 105, 43),
    Instrument(521, "Rabab", 105, 44),
    Instrument(522, "Kemenche", 110, 44),
    Instrument(523, "Ney 1", 72, 10),
    Instrument(524, "Ney 2", 72, 41),
    Instrument(525, "Zurna", 111, 9),
    Instrument(526, "ArabcOrg", 16, 7),
    Instrument(527, "ArabcStr", 48, 7),
    Instrument(528, "Er Hu 1", 110, 9),
    Instrument(529, "Er Hu 2", 110, 40),
    Instrument(530, "Er Hu 3", 110, 41),
    Instrument(531, "Er Hu 4", 110, 42),
    Instrument(532, "YangQin1", 15, 2),
    Instrument(533, "YangQin2", 15, 3),
    Instrument(534, "YangQin3", 15, 34),
    Instrument(535, "Zheng 1", 107, 8),
    Instrument(536, "Zheng 2", 107, 40),
    Instrument(537, "Pi Pa 1", 105, 8),
    Instrument(538, "Pi Pa 2", 105, 9),
    Instrument(539, "Pi Pa 3", 105, 40),
    Instrument(540, "ChinsHrp", 46, 33),
    Instrument(541, "Di Zi 1", 72, 8),
    Instrument(542, "Di Zi 2", 72, 40),
    Instrument(543, "Xiao", 77, 8),
    Instrument(544, "Sheng 1", 109, 8),
    Instrument(545, "Sheng 2", 109, 40),
    Instrument(546, "Suo Na 1", 111, 10),
    Instrument(547, "Suo Na 2", 111, 32),
    Instrument(548, "Cavquinh", 104, 38),
    Instrument(549, "ViolCapr", 104, 39),
    Instrument(550, "Berimbau", 104, 40),
    Instrument(551, "Pandeiro", 116, 40),
    Instrument(552, "Banjo", 105, 32),
    Instrument(553, "MuteBnjo", 105, 1),
    Instrument(554, "SteelDrm", 114, 1),
    Instrument(555, "Fiddle 1", 110, 32),
    Instrument(556, "Shamisen", 106, 32),
    Instrument(557, "Koto", 107, 32),
    Instrument(558, "ThumbPno", 108, 32),
    Instrument(559, "Bagpipe", 109, 32),
    Instrument(560, "Fiddle 2", 110, 33),
    Instrument(561, "Piano1 G", 0, 0),
    Instrument(562, "Piano2 G", 1, 0),
    Instrument(563, "E.GrandG", 2, 0),
    Instrument(564, "HonkyT.G", 3, 0),
    Instrument(565, "E.Pno1 G", 4, 0),
    Instrument(566, "E.Pno2 G", 5, 0),
    Instrument(567, "Harpsi.G", 6, 0),
    Instrument(568, "Clavi G", 7, 0),
    Instrument(569, "CelestaG", 8, 0),
    Instrument(570, "GlockenG", 9, 0),
    Instrument(571, "MusicB.G", 10, 0),
    Instrument(572, "Vibes G", 11, 0),
    Instrument(573, "MarimbaG", 12, 0),
    Instrument(574, "XylophnG", 13, 0),
    Instrument(575, "TublrB.G", 14, 0),
    Instrument(576, "DulcimrG", 15, 0),
    Instrument(577, "Organ1 G", 16, 0),
    Instrument(578, "Organ2 G", 17, 0),
    Instrument(579, "Organ3 G", 18, 0),
    Instrument(580, "PipeOrgG", 19, 0),
    Instrument(581, "ReedOrgG", 20, 0),
    Instrument(582, "AcordonG", 21, 0),
    Instrument(583, "HrmnicaG", 22, 0),
    Instrument(584, "BndneonG", 23, 0),
    Instrument(585, "NylonGtG", 24, 0),
    Instrument(586, "SteelGtG", 25, 0),
    Instrument(587, "JazzGt G", 26, 0),
    Instrument(588, "CleanGtG", 27, 0),
    Instrument(589, "MuteGt G", 28, 0),
    Instrument(590, "Ovd Gt G", 29, 0),
    Instrument(591, "DistGt G", 30, 0),
    Instrument(592, "GtHrmncG", 31, 0),
    Instrument(593, "AcousBsG", 32, 0),
    Instrument(594, "FingrBsG", 33, 0),
    Instrument(595, "PickBs G", 34, 0),
    Instrument(596, "FrtlsBsG", 35, 0),
    Instrument(597, "SlpBs1 G", 36, 0),
    Instrument(598, "SlpBs2 G", 37, 0),
    Instrument(599, "SynBs1 G", 38, 0),
    Instrument(600, "SynBs2 G", 39, 0),
    Instrument(601, "Violin G", 40, 0),
    Instrument(602, "Viola G", 41, 0),
    Instrument(603, "Cello G", 42, 0),
    Instrument(604, "ContrbsG", 43, 0),
    Instrument(605, "TremStrG", 44, 0),
    Instrument(606, "PizzcatG", 45, 0),
    Instrument(607, "Harp G", 46, 0),
    Instrument(608, "TimpaniG", 47, 0),
    Instrument(609, "String1G", 48, 0),
    Instrument(610, "String2G", 49, 0),
    Instrument(611, "SynStr1G", 50, 0),
    Instrument(612, "SynStr2G", 51, 0),
    Instrument(613, "Choir G", 52, 0),
    Instrument(614, "VoiDoo G", 53, 0),
    Instrument(615, "SynVoi.G", 54, 0),
    Instrument(616, "OrcHit G", 55, 0),
    Instrument(617, "TrumpetG", 56, 0),
    Instrument(618, "TrombonG", 57, 0),
    Instrument(619, "Tuba G", 58, 0),
    Instrument(620, "MuteTrpG", 59, 0),
    Instrument(621, "FrHorn G", 60, 0),
    Instrument(622, "Brass G", 61, 0),
    Instrument(623, "SynBrs1G", 62, 0),
    Instrument(624, "SynBrs2G", 63, 0),
    Instrument(625, "S.Sax G", 64, 0),
    Instrument(626, "A.Sax G", 65, 0),
    Instrument(627, "T.Sax G", 66, 0),
    Instrument(628, "B.Sax G", 67, 0),
    Instrument(629, "Oboe G", 68, 0),
    Instrument(630, "E.Horn G", 69, 0),
    Instrument(631, "BassoonG", 70, 0),
    Instrument(632, "ClarnetG", 71, 0),
    Instrument(633, "PiccoloG", 72, 0),
    Instrument(634, "Flute G", 73, 0),
    Instrument(635, "RecordrG", 74, 0),
    Instrument(636, "PanFlt G", 75, 0),
    Instrument(637, "BotlBlwG", 76, 0),
    Instrument(638, "ShkhchiG", 77, 0),
    Instrument(639, "WhistleG", 78, 0),
    Instrument(640, "OcarinaG", 79, 0),
    Instrument(641, "SqrLeadG", 80, 0),
    Instrument(642, "SawLeadG", 81, 0),
    Instrument(643, "CaliopeG", 82, 0),
    Instrument(644, "ChiffLdG", 83, 0),
    Instrument(645, "CharangG", 84, 0),
    Instrument(646, "VoiceLdG", 85, 0),
    Instrument(647, "FifthLdG", 86, 0),
    Instrument(648, "Bs+LeadG", 87, 0),
    Instrument(649, "FantasyG", 88, 0),
    Instrument(650, "WarmPadG", 89, 0),
    Instrument(651, "PolySynG", 90, 0),
    Instrument(652, "SpacChoG", 91, 0),
    Instrument(653, "BowGlasG", 92, 0),
    Instrument(654, "MetalPdG", 93, 0),
    Instrument(655, "HaloPadG", 94, 0),
    Instrument(656, "SweepPdG", 95, 0),
    Instrument(657, "RainDrpG", 96, 0),
    Instrument(658, "SoundTrG", 97, 0),
    Instrument(659, "CrystalG", 98, 0),
    Instrument(660, "AtmosphG", 99, 0),
    Instrument(661, "BritnesG", 100, 0),
    Instrument(662, "GoblinsG", 101, 0),
    Instrument(663, "Echoes G", 102, 0),
    Instrument(664, "SF G", 103, 0),
    Instrument(665, "Sitar G", 104, 0),
    Instrument(666, "Banjo G", 105, 0),
    Instrument(667, "ShamisnG", 106, 0),
    Instrument(668, "Koto G", 107, 0),
    Instrument(669, "ThumbP.G", 108, 0),
    Instrument(670, "BagpipeG", 109, 0),
    Instrument(671, "Fiddle G", 110, 0),
    Instrument(672, "Shanai G", 111, 0),
    Instrument(673, "TinklBlG", 112, 0),
    Instrument(674, "Agogo G", 113, 0),
    Instrument(675, "SteelDrG", 114, 0),
    Instrument(676, "WodBlokG", 115, 0),
    Instrument(677, "Taiko G", 116, 0),
    Instrument(678, "MeloTomG", 117, 0),
    Instrument(679, "SynDrumG", 118, 0),
    Instrument(680, "RevCym.G", 119, 0),
    Instrument(681, "FrNoiseG", 120, 0),
    Instrument(682, "BrNoiseG", 121, 0),
    Instrument(683, "SeashorG", 122, 0),
    Instrument(684, "Bird G", 123, 0),
    Instrument(685, "TelphonG", 124, 0),
    Instrument(686, "HelcptrG", 125, 0),
    Instrument(687, "AplauseG", 126, 0),
    Instrument(688, "GunshotG", 127, 0),
    Instrument(689, "Piano E", 0, 80),
    Instrument(690, "HnkyTnkE", 1, 80),
    Instrument(691, "Harpsi.E", 2, 80),
    Instrument(692, "E.PianoE", 3, 80),
    Instrument(693, "Clavi E", 4, 80),
    Instrument(694, "WahClavE", 5, 80),
    Instrument(695, "Vibes E", 6, 80),
    Instrument(696, "CelestaE", 7, 80),
    Instrument(697, "MarimbaE", 8, 80),
    Instrument(698, "XylophnE", 9, 80),
    Instrument(699, "Organ E", 10, 80),
    Instrument(700, "JazzOrgE", 11, 80),
    Instrument(701, "TheatreE", 12, 80),
    Instrument(702, "AcordonE", 13, 80),
    Instrument(703, "MusetteE", 14, 80),
    Instrument(704, "HrmnicaE", 15, 80),
    Instrument(705, "Guitar E", 16, 80),
    Instrument(706, "ClascGtE", 17, 80),
    Instrument(707, "AcousGtE", 18, 80),
    Instrument(708, "FolkGt E", 19, 80),
    Instrument(709, "JazzGt E", 20, 80),
    Instrument(710, "Elec.GtE", 21, 80),
    Instrument(711, "LeadGt E", 22, 80),
    Instrument(712, "MandolnE", 23, 80),
    Instrument(713, "Bass E", 24, 80),
    Instrument(714, "StringsE", 25, 80),
    Instrument(715, "SlowStrE", 26, 80),
    Instrument(716, "MarcatoE", 27, 80),
    Instrument(717, "Trm.StrE", 28, 80),
    Instrument(718, "Piz.StrE", 29, 80),
    Instrument(719, "Orch. E", 30, 80),
    Instrument(720, "Violin E", 31, 80),
    Instrument(721, "Cello E", 32, 80),
    Instrument(722, "Harp E", 33, 80),
    Instrument(723, "Brass E", 34, 80),
    Instrument(724, "BrasEnsE", 35, 80),
    Instrument(725, "BrsSectE", 36, 80),
    Instrument(726, "TrumpetE", 37, 80),
    Instrument(727, "TrombonE", 38, 80),
    Instrument(728, "Horn E", 39, 80),
    Instrument(729, "Horns E", 40, 80),
    Instrument(730, "SoprSaxE", 41, 80),
    Instrument(731, "AltoSaxE", 42, 80),
    Instrument(732, "T.Sax E", 43, 80),
    Instrument(733, "SaxophnE", 44, 80),
    Instrument(734, "Sax. E", 45, 80),
    Instrument(735, "Sax E", 46, 80),
    Instrument(736, "SaxEns.E", 47, 80),
    Instrument(737, "Sax.SctE", 48, 80),
    Instrument(738, "Oboe E", 49, 80),
    Instrument(739, "BassoonE", 50, 80),
    Instrument(740, "ClarnetE", 51, 80),
    Instrument(741, "PiccoloE", 52, 80),
    Instrument(742, "Flute E", 53, 80),
    Instrument(743, "PanFlutE", 54, 80),
    Instrument(744, "WhistleE", 55, 80),
    Instrument(745, "WodwindE", 56, 80),
    Instrument(746, "Synth E", 57, 80),
    Instrument(747, "Lead E", 58, 80),
    Instrument(748, "SynLeadE", 59, 80),
    Instrument(749, "SqrLeadE", 60, 80),
    Instrument(750, "SawLeadE", 61, 80),
    Instrument(751, "HipLeadE", 62, 80),
    Instrument(752, "HopLeadE", 63, 80),
    Instrument(753, "PopLeadE", 64, 80),
    Instrument(754, "FrWr E", 65, 80),
    Instrument(755, "WireLd E", 66, 80),
    Instrument(756, "Pad E", 67, 80),
    Instrument(757, "Fntsia E", 68, 80),
    Instrument(758, "XenonPdE", 69, 80),
    Instrument(759, "Choir E", 70, 80),
    Instrument(760, "Sitar E", 71, 80),
    Instrument(761, "Banjo E", 72, 80),
    Instrument(762, "Fiddle E", 73, 80),
    Instrument(763, "StelDrmE", 74, 80),
    Instrument(764, "StandrdE", 75, 120),
    Instrument(765, "Standrd1", 0, 120),
    Instrument(766, "Standrd2", 1, 120),
    Instrument(767, "Standrd3", 2, 120),
    Instrument(768, "Standrd4", 3, 120),
    Instrument(769, "Standrd5", 4, 120),
    Instrument(770, "Dance 1", 26, 120),
    Instrument(771, "Dance 2", 27, 120),
    Instrument(772, "Dance 3", 28, 120),
    Instrument(773, "Dance 4", 29, 120),
    Instrument(774, "Dance 5", 34, 120),
    Instrument(775, "Dance 6", 35, 120),
    Instrument(776, "TrnceSet", 31, 120),
    Instrument(777, "HipHpSet", 9, 120),
    Instrument(778, "Room Set", 8, 120),
    Instrument(779, "PowerSet", 16, 120),
    Instrument(780, "Rock Set", 17, 120),
    Instrument(781, "Elec.Set", 24, 120),
    Instrument(782, "DrmMchn1", 25, 120),
    Instrument(783, "DrmMchn2", 30, 120),
    Instrument(784, "DrmMchn3", 33, 120),
    Instrument(785, "Jazz Set", 32, 120),
    Instrument(786, "BrushSet", 40, 120),
    Instrument(787, "Orch.Set", 48, 120),
    Instrument(788, "LatinSt1", 49, 120),
    Instrument(789, "LatinSt2", 50, 120),
    Instrument(790, "IndnsaSt", 53, 120),
    Instrument(791, "IndianSt", 54, 120),
    Instrument(792, "ArabicSt", 52, 120),
    Instrument(793, "ChinesSt", 51, 120),
    Instrument(794, "Sfx Set1", 60, 120),
    Instrument(795, "Sfx Set2", 61, 120),
    Instrument(796, "SnareSt1", 64, 120),
    Instrument(797, "SnareSt2", 65, 120),
    Instrument(798, "Kick Set", 66, 120),
    Instrument(799, "CymbalSt", 67, 120),
    Instrument(800, "Tom Set", 68, 120),
    Instrument(801, "User 000", 0, 65),
    Instrument(802, "User 001", 1, 65),
    Instrument(803, "User 002", 2, 65),
    Instrument(804, "User 003", 3, 65),
    Instrument(805, "User 004", 4, 65),
    Instrument(806, "User 005", 5, 65),
    Instrument(807, "User 006", 6, 65),
    Instrument(808, "User 007", 7, 65),
    Instrument(809, "User 008", 8, 65),
    Instrument(810, "User 009", 9, 65),
    Instrument(811, "User 010", 10, 65),
    Instrument(812, "User 011", 11, 65),
    Instrument(813, "User 012", 12, 65),
    Instrument(814, "User 013", 13, 65),
    Instrument(815, "User 014", 14, 65),
    Instrument(816, "User 015", 15, 65),
    Instrument(817, "User 016", 16, 65),
    Instrument(818, "User 017", 17, 65),
    Instrument(819, "User 018", 18, 65),
    Instrument(820, "User 019", 19, 65),
    Instrument(821, "User 020", 20, 65),
    Instrument(822, "User 021", 21, 65),
    Instrument(823, "User 022", 22, 65),
    Instrument(824, "User 023", 23, 65),
    Instrument(825, "User 024", 24, 65),
    Instrument(826, "User 025", 25, 65),
    Instrument(827, "User 026", 26, 65),
    Instrument(828, "User 027", 27, 65),
    Instrument(829, "User 028", 28, 65),
    Instrument(830, "User 029", 29, 65),
    Instrument(831, "User 030", 30, 65),
    Instrument(832, "User 031", 31, 65),
    Instrument(833, "User 032", 32, 65),
    Instrument(834, "User 033", 33, 65),
    Instrument(835, "User 034", 34, 65),
    Instrument(836, "User 035", 35, 65),
    Instrument(837, "User 036", 36, 65),
    Instrument(838, "User 037", 37, 65),
    Instrument(839, "User 038", 38, 65),
    Instrument(840, "User 039", 39, 65),
    Instrument(841, "User 040", 40, 65),
    Instrument(842, "User 041", 41, 65),
    Instrument(843, "User 042", 42, 65),
    Instrument(844, "User 043", 43, 65),
    Instrument(845, "User 044", 44, 65),
    Instrument(846, "User 045", 45, 65),
    Instrument(847, "User 046", 46, 65),
    Instrument(848, "User 047", 47, 65),
    Instrument(849, "User 048", 48, 65),
    Instrument(850, "User 049", 49, 65),
    Instrument(851, "User 050", 50, 65),
    Instrument(852, "User 051", 51, 65),
    Instrument(853, "User 052", 52, 65),
    Instrument(854, "User 053", 53, 65),
    Instrument(855, "User 054", 54, 65),
    Instrument(856, "User 055", 55, 65),
    Instrument(857, "User 056", 56, 65),
    Instrument(858, "User 057", 57, 65),
    Instrument(859, "User 058", 58, 65),
    Instrument(860, "User 059", 59, 65),
    Instrument(861, "User 060", 60, 65),
    Instrument(862, "User 061", 61, 65),
    Instrument(863, "User 062", 62, 65),
    Instrument(864, "User 063", 63, 65),
    Instrument(865, "User 064", 64, 65),
    Instrument(866, "User 065", 65, 65),
    Instrument(867, "User 066", 66, 65),
    Instrument(868, "User 067", 67, 65),
    Instrument(869, "User 068", 68, 65),
    Instrument(870, "User 069", 69, 65),
    Instrument(871, "User 070", 70, 65),
    Instrument(872, "User 071", 71, 65),
    Instrument(873, "User 072", 72, 65),
    Instrument(874, "User 073", 73, 65),
    Instrument(875, "User 074", 74, 65),
    Instrument(876, "User 075", 75, 65),
    Instrument(877, "User 076", 76, 65),
    Instrument(878, "User 077", 77, 65),
    Instrument(879, "User 078", 78, 65),
    Instrument(880, "User 079", 79, 65),
    Instrument(881, "User 080", 80, 65),
    Instrument(882, "User 081", 81, 65),
    Instrument(883, "User 082", 82, 65),
    Instrument(884, "User 083", 83, 65),
    Instrument(885, "User 084", 84, 65),
    Instrument(886, "User 085", 85, 65),
    Instrument(887, "User 086", 86, 65),
    Instrument(888, "User 087", 87, 65),
    Instrument(889, "User 088", 88, 65),
    Instrument(890, "User 089", 89, 65),
    Instrument(891, "User 090", 90, 65),
    Instrument(892, "User 091", 91, 65),
    Instrument(893, "User 092", 92, 65),
    Instrument(894, "User 093", 93, 65),
    Instrument(895, "User 094", 94, 65),
    Instrument(896, "User 095", 95, 65),
    Instrument(897, "User 096", 96, 65),
    Instrument(898, "User 097", 97, 65),
    Instrument(899, "User 098", 98, 65),
    Instrument(900, "User 099", 99, 65)
)
