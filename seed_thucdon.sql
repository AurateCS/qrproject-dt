-- ============================================================
-- Thực Đơn Seed – 14-day rotating cycle
-- 7 canteens, 2 choices Sáng + 3 choices Trưa per day = 490 rows
-- Paired canteens (VT001/VT002, VT003/VT004, VT006/VT007) share
-- the same dish pool but are offset so they differ day-to-day.
-- ============================================================

TRUNCATE TABLE thucdon RESTART IDENTITY;

INSERT INTO thucdon
  ("MaViTri","ChuKyNgay","BuaAn","MaMonAn",
   "ThoiGianBatDau","SoSuatDuKien","TrangThai",
   "NgayTao","NguoiTao","NgaySua","NguoiSua")
VALUES

-- ══════════════════════════════════════════════════════════════
-- VT001 · Căng tin tầng 1 - Thịnh Phát
-- Sáng pool: MA004 Phở bò, MA005 Bánh mì thịt nguội, MA012 Bánh mì sandwich gà
--            MA015 Phở gà, MA019 Xôi gà, MA024 Bánh mì chả cá
-- Trưa pool: MA001 Cơm sườn bì chả, MA002 Cơm gà xôi mỡ, MA006 Cơm tấm sườn trứng
--            MA011 Salad, MA014 Cơm sườn đặc biệt, MA023 Cơm hộp kho vàng
-- ══════════════════════════════════════════════════════════════
('VT001',1,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',1,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',1,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',1,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',1,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',2,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',2,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',2,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',2,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',2,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',3,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',3,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',3,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',3,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',3,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',4,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',4,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',4,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',4,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',4,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',5,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',5,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',5,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',5,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',5,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',6,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',6,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',6,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',6,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',6,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',7,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',7,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',7,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',7,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',7,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',8,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',8,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',8,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',8,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',8,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',9,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',9,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',9,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',9,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',9,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',10,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',10,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',10,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',10,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',10,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',11,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',11,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',11,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',11,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',11,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',12,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',12,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',12,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',12,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',12,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',13,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',13,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',13,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',13,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',13,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT001',14,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',14,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT001',14,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',14,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT001',14,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

-- ══════════════════════════════════════════════════════════════
-- VT002 · Căng tin tầng 3 - Thịnh Phát  (same pool as VT001, offset by 1)
-- ══════════════════════════════════════════════════════════════
('VT002',1,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',1,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',1,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',1,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',1,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',2,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',2,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',2,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',2,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',2,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',3,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',3,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',3,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',3,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',3,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',4,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',4,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',4,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',4,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',4,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',5,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',5,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',5,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',5,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',5,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',6,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',6,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',6,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',6,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',6,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',7,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',7,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',7,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',7,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',7,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',8,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',8,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',8,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',8,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',8,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',9,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',9,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',9,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',9,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',9,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',10,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',10,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',10,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',10,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',10,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',11,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',11,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',11,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',11,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',11,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',12,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',12,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',12,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',12,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',12,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',13,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',13,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',13,'Trưa','MA002','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',13,'Trưa','MA006','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',13,'Trưa','MA014','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT002',14,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',14,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT002',14,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',14,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT002',14,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

-- ══════════════════════════════════════════════════════════════
-- VT003 · Phòng ăn tòa nhà A - VN Tech
-- Sáng pool: MA004 Phở bò, MA008 Hủ tiếu, MA012 Bánh mì sandwich
--            MA015 Phở gà, MA016 Bánh cuốn thịt, MA019 Xôi gà
-- Trưa pool: MA007 Mì xào hải sản, MA009 Cơm chiên Dương Châu,
--            MA010 Cơm văn phòng 3 món, MA011 Salad, MA013 Bún thịt nướng, MA023 Cơm hộp kho vàng
-- ══════════════════════════════════════════════════════════════
('VT003',1,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',1,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',1,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',1,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',1,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',2,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',2,'Sáng','MA016','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',2,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',2,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',2,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',3,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',3,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',3,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',3,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',3,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',4,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',4,'Sáng','MA016','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',4,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',4,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',4,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',5,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',5,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',5,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',5,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',5,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',6,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',6,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',6,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',6,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',6,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',7,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',7,'Sáng','MA016','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',7,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',7,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',7,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',8,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',8,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',8,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',8,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',8,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',9,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',9,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',9,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',9,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',9,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',10,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',10,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',10,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',10,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',10,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',11,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',11,'Sáng','MA016','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',11,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',11,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',11,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',12,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',12,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',12,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',12,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',12,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',13,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',13,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',13,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',13,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',13,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT003',14,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',14,'Sáng','MA016','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT003',14,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',14,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT003',14,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

-- ══════════════════════════════════════════════════════════════
-- VT004 · Phòng ăn tòa nhà B - VN Tech  (same pool as VT003, offset by 1)
-- ══════════════════════════════════════════════════════════════
('VT004',1,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',1,'Sáng','MA016','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',1,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',1,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',1,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',2,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',2,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',2,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',2,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',2,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',3,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',3,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',3,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',3,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',3,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',4,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',4,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',4,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',4,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',4,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',5,'Sáng','MA016','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',5,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',5,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',5,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',5,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',6,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',6,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',6,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',6,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',6,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',7,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',7,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',7,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',7,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',7,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',8,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',8,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',8,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',8,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',8,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',9,'Sáng','MA016','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',9,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',9,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',9,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',9,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',10,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',10,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',10,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',10,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',10,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',11,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',11,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',11,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',11,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',11,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',12,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',12,'Sáng','MA016','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',12,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',12,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',12,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',13,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',13,'Sáng','MA015','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',13,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',13,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',13,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT004',14,'Sáng','MA004','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',14,'Sáng','MA012','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT004',14,'Trưa','MA007','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',14,'Trưa','MA010','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT004',14,'Trưa','MA011','11:30',80,'active',NOW(),'system',NOW(),'system'),

-- ══════════════════════════════════════════════════════════════
-- VT005 · Căng tin xưởng may - Phương Nam
-- Sáng pool: MA003 Bún bò Huế, MA005 Bánh mì thịt nguội, MA008 Hủ tiếu
--            MA018 Bún riêu cua, MA019 Xôi gà, MA024 Bánh mì chả cá
-- Trưa pool: MA001 Cơm sườn bì chả, MA009 Cơm chiên Dương Châu,
--            MA017 Cơm công nhân 4 món, MA020 Cơm nhà máy 3 món
-- ══════════════════════════════════════════════════════════════
('VT005',1,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',1,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',1,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',1,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',1,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',2,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',2,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',2,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',2,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',2,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',3,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',3,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',3,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',3,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',3,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',4,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',4,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',4,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',4,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',4,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',5,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',5,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',5,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',5,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',5,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',6,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',6,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',6,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',6,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',6,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',7,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',7,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',7,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',7,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',7,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',8,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',8,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',8,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',8,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',8,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',9,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',9,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',9,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',9,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',9,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',10,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',10,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',10,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',10,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',10,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',11,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',11,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',11,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',11,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',11,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',12,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',12,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',12,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',12,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',12,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',13,'Sáng','MA005','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',13,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',13,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',13,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',13,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT005',14,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',14,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT005',14,'Trưa','MA009','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',14,'Trưa','MA001','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT005',14,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

-- ══════════════════════════════════════════════════════════════
-- VT006 · Nhà ăn nhà máy - Đại Dương
-- Sáng pool: MA003 Bún bò Huế, MA008 Hủ tiếu, MA018 Bún riêu cua
--            MA019 Xôi gà, MA021 Cháo lòng heo, MA024 Bánh mì chả cá
-- Trưa pool: MA013 Bún thịt nướng, MA017 Cơm công nhân 4 món,
--            MA020 Cơm nhà máy 3 món, MA023 Cơm hộp kho vàng
-- ══════════════════════════════════════════════════════════════
('VT006',1,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',1,'Sáng','MA021','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',1,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',1,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',1,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',2,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',2,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',2,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',2,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',2,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',3,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',3,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',3,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',3,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',3,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',4,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',4,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',4,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',4,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',4,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',5,'Sáng','MA021','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',5,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',5,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',5,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',5,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',6,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',6,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',6,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',6,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',6,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',7,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',7,'Sáng','MA021','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',7,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',7,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',7,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',8,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',8,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',8,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',8,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',8,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',9,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',9,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',9,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',9,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',9,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',10,'Sáng','MA021','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',10,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',10,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',10,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',10,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',11,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',11,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',11,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',11,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',11,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',12,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',12,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',12,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',12,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',12,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',13,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',13,'Sáng','MA021','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',13,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',13,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',13,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT006',14,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',14,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT006',14,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',14,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT006',14,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

-- ══════════════════════════════════════════════════════════════
-- VT007 · Khu vực kho - Đại Dương  (same pool as VT006, offset by 1)
-- ══════════════════════════════════════════════════════════════
('VT007',1,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',1,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',1,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',1,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',1,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',2,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',2,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',2,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',2,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',2,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',3,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',3,'Sáng','MA021','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',3,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',3,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',3,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',4,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',4,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',4,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',4,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',4,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',5,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',5,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',5,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',5,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',5,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',6,'Sáng','MA021','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',6,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',6,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',6,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',6,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',7,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',7,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',7,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',7,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',7,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',8,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',8,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',8,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',8,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',8,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',9,'Sáng','MA021','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',9,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',9,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',9,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',9,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',10,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',10,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',10,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',10,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',10,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',11,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',11,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',11,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',11,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',11,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',12,'Sáng','MA021','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',12,'Sáng','MA024','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',12,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',12,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',12,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',13,'Sáng','MA003','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',13,'Sáng','MA018','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',13,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',13,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',13,'Trưa','MA017','11:30',80,'active',NOW(),'system',NOW(),'system'),

('VT007',14,'Sáng','MA008','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',14,'Sáng','MA019','07:00',50,'active',NOW(),'system',NOW(),'system'),
('VT007',14,'Trưa','MA023','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',14,'Trưa','MA020','11:30',80,'active',NOW(),'system',NOW(),'system'),
('VT007',14,'Trưa','MA013','11:30',80,'active',NOW(),'system',NOW(),'system');
