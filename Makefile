SRCDIR			= ./src
MPI_SRCDIR		= ./mpi_src
OMP_SRCDIR		= ./omp_src
INCLUDEDIR		= ./include

NORMAL_OBJDIR	= obj/normal
MPI_OBJDIR		= obj/mpi
OMP_OBJDIR		= obj/openmp

SRC				= $(SRCDIR)/func.cpp $(SRCDIR)/main.cpp
MPI_SRC			= $(MPI_SRCDIR)/func.cpp $(MPI_SRCDIR)/main.cpp
OMP_SRC			= $(OMP_SRCDIR)/func.cpp $(OMP_SRCDIR)/main.cpp

# Nom des binaires
NAME_NORMAL		= project
NAME_MPI		= project_mpi
NAME_OMP		= project_omp

# Compilateurs
CXX_NORMAL		= g++
CXX_MPI			= mpic++
CXX_OMP			= g++

# Flags communs
CFLAGS			= -Wall -Wextra -Werror -O3 -ftree-vectorize
INCLUDEFLAGS	= -I$(INCLUDEDIR)

# Flags spécifiques
CFLAGS_MPI		= -DMPICH_SKIP_MPICXX -DOMPI_SKIP_MPICXX
CFLAGS_OMP		= -fopenmp

# Fichiers objets
OBJ_NORMAL		= $(SRC:$(SRCDIR)/%.cpp=$(NORMAL_OBJDIR)/%.o)
OBJ_MPI			= $(MPI_SRC:$(MPI_SRCDIR)/%.cpp=$(MPI_OBJDIR)/%.o)
OBJ_OMP			= $(OMP_SRC:$(OMP_SRCDIR)/%.cpp=$(OMP_OBJDIR)/%.o)

# Compilation de chaque fichier objet
$(NORMAL_OBJDIR)/%.o: $(SRCDIR)/%.cpp
	@mkdir -p $(dir $@)
	$(CXX_NORMAL) -MD $(CFLAGS) $(INCLUDEFLAGS) -c $< -o $@

$(MPI_OBJDIR)/%.o: $(MPI_SRCDIR)/%.cpp
	@mkdir -p $(dir $@)
	$(CXX_MPI) -MD $(CFLAGS) $(CFLAGS_MPI) $(INCLUDEFLAGS) -c $< -o $@

$(OMP_OBJDIR)/%.o: $(OMP_SRCDIR)/%.cpp
	@mkdir -p $(dir $@)
	$(CXX_OMP) -MD $(CFLAGS) $(CFLAGS_OMP) $(INCLUDEFLAGS) -c $< -o $@

# Cibles finales
$(NAME_NORMAL): $(OBJ_NORMAL)
	@echo -e "\033[1;32m[Normal] Compilation de $(NAME_NORMAL)\033[0m"
	$(CXX_NORMAL) -o $@ $^ $(CFLAGS) $(INCLUDEFLAGS)

$(NAME_MPI): $(OBJ_MPI)
	@echo -e "\033[1;34m[MPI] Compilation de $(NAME_MPI)\033[0m"
	$(CXX_MPI) -o $@ $^ $(CFLAGS) $(CFLAGS_MPI) $(INCLUDEFLAGS)

$(NAME_OMP): $(OBJ_OMP)
	@echo -e "\033[1;35m[OpenMP] Compilation de $(NAME_OMP)\033[0m"
	$(CXX_OMP) -o $@ $^ $(CFLAGS) $(CFLAGS_OMP) $(INCLUDEFLAGS)

# Compilation individuelle
normal:	$(NAME_NORMAL)
mpi:	$(NAME_MPI)
omp:	$(NAME_OMP)

# Compilation de tout
all: normal mpi omp

clean:
	@echo -e "\033[1;31mNettoyage des fichiers objets\033[0m"
	rm -rf obj

fclean: clean
	@echo -e "\033[1;31mNettoyage des binaires\033[0m"
	rm -f $(NAME_NORMAL) $(NAME_MPI) $(NAME_OMP)
	rm -f *.gcda *.gcno *vgcore.*

re:	fclean all

# Inclusion des fichiers de dépendance
-include $(OBJ_NORMAL:%.o=%.d) $(OBJ_MPI:%.o=%.d) $(OBJ_OMP:%.o=%.d)

# Compilation of the LaTeX report
report:
	@echo -e "\033[1;36m[LaTeX] Compilation of report/report.tex\033[0m"
	cd report && pdflatex -interaction=nonstopmode report.tex
	cd report && pdflatex -interaction=nonstopmode report.tex
	@echo -e "\033[1;32m[LaTeX] report.pdf generated successfully.\033[0m"

report-clean:
	@echo -e "\033[1;31m[LaTeX] Cleaning auxiliary files\033[0m"
	rm -f report/*.aux report/*.log report/*.out report/*.toc report/*.lof report/*.lot report/*.synctex.gz

report-fclean: report-clean
	rm -f report/report.pdf

.PHONY:	all normal mpi omp clean fclean re report report-clean report-fclean

