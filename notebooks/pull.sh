declare -a cells=("T34U[DEF]G" "T34V[DEF][HJK]" "T35U[LM]B" "T35V[LM][CDE]")
declare -a channels=("B0[48]" "SCL")

for i in "${cells[@]}"
do
    for j in "${channels[@]}"
    do
        scp "kristaps@192.168.72.196:/home/kristaps/Projs/bulbulis/notebooks/data/${i}_202[12]*${j}*" data/
    done
done
