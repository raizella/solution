%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% computePageRank.m
%
% Reads in an adjacency matrix produced by
% buildAdjacency.py and writes the resulting
% page rank scores to the file pageRank.dat.
%
% Should be called from the command line by
% ./computePageRank.sh
%
% Authors: David Storch (dstorch)
%          Matt Mahoney (mjmahone
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% SET PARAMETERS HERE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% number of powers to compute for markov chain
I = 128;
% damping factor (or, teleport probability)
alpha = 0.1;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% load sparse matrix from file
load adjacency.dat
adjacency = spconvert(adjacency);

% get dimensions of sparse matrix
nm = size(adjacency);
N = nm(1);

alphaN = alpha / N;
oneN = 1 / N;

% initializations
x = zeros(1, N);
x(1) = 1;
binvec = zeros(1, N);

% initialize the binary vector
sumvec = sum(adjacency, 2);
for k=1:N
   if sumvec(k) == 0
       binvec(k) = 1;
   end
end

% main loop for page rank computation
for i=1:I

    v = 0;
    for k=1:N
        if binvec(k) == 0
            v = v + (alphaN * x(k));
        elseif binvec(k) == 1
            v = v + (oneN * x(k));
        end
    end
    
    x = ((1 - alpha) * x * adjacency) + v;
end

% output results to a file
fid = fopen('pageRank.dat', 'w');

for i=1:N
   fprintf(fid, '%12.16f\n', x(i));
end

fclose(fid);

