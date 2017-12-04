
delete from mysql.user where host!='127.0.0.1' or user!='root';
flush privileges;

grant process,reload,lock tables,super,replication client,replication slave on *.* to 'bkpuser'@'127.0.0.1' identified by password '*2a58dd5a959b1b5d320404c21b42bbc69ac0defe';
grant select,insert,update,create on percona_schema.* to 'bkpuser'@'127.0.0.1';
grant process,reload,lock tables,super,replication client,replication slave on *.* to 'bkpuser'@'localhost' identified by password '*2a58dd5a959b1b5d320404c21b42bbc69ac0defe';
grant select,insert,update,create on percona_schema.* to 'bkpuser'@'localhost';

grant replication client, process on *.* to falcon@'127.0.0.1' identified by password '*fcf759487eb0b555e9a59da3c17db0957b52aca6';

grant process, super on *.* to 'lepus_monitor'@'192.168.40.65' identified by password '*4d4c3f19988186783d5d44e42b448a2ccd5d78e5';
grant select, insert, update, delete, create, alter, super, replication slave, replication client on *.* to 'putin_rw'@'172.16.33.191' identified by password '*a6359871933ad9553787adadfdcc3bdbc7445233';

grant all on *.* to tianyuan@'127.0.0.1' identified by password '*efc0f6a55d04b7d11330b7e3c3234b14d1b9be3c' with grant option;
grant all on *.* to tianyuan@'192.168.40.65' identified by password '*efc0f6a55d04b7d11330b7e3c3234b14d1b9be3c' with grant option;
reset master;
grant all on *.* to root@'127.0.0.1' identified by password '*2eada92e1de4822686100c544d7d5e88ac27fb15' with grant option;